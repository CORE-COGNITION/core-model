"""Laplace log marginal likelihood for a trained model
(https://aleximmer.com/Laplace/).

Fits an **all-parameter diagonal** Gaussian posterior around the trained (MAP)
weights and reports the Laplace **log marginal likelihood**.

"""

import torch
import torch.nn.functional as F
from torch.nn.utils import parameters_to_vector
from torch.utils.data import DataLoader

class DiagLaplaceEF:
    def __init__(self, model):
        self.params = [p for p in model.parameters() if p.requires_grad]
        self.n_params = sum(p.numel() for p in self.params)
        self.n_layers = len(self.params)
        self.device = self.params[0].device
        self.dtype = torch.float32
        self.mean = None        # (n_params,) MAP weights
        self.H = None           # (n_params,) diagonal curvature (empirical Fisher)
        self.loss = 0.0         # summed NLL over the fit data
        self._prior_precision = torch.ones(1, device=self.device, dtype=self.dtype)

    @property
    def prior_precision(self):
        return self._prior_precision

    @prior_precision.setter
    def prior_precision(self, value):
        if not isinstance(value, torch.Tensor):
            value = torch.as_tensor(value)
        self._prior_precision = value.reshape(-1).to(device=self.device, dtype=self.dtype)

    @property
    def prior_precision_diag(self):
        """Expand per-layer prior precision to (n_params,)."""
        pp = self._prior_precision
        if pp.numel() == 1:
            return pp * torch.ones(self.n_params, device=self.device, dtype=self.dtype)
        if pp.numel() == self.n_layers:
            return torch.cat([
                pp[i] * torch.ones(p.numel(), device=self.device, dtype=self.dtype)
                for i, p in enumerate(self.params)
            ])
        raise ValueError("prior_precision length != scalar / n_layers")

    def log_marginal_likelihood(self, prior_precision=None):
        if prior_precision is not None:
            self.prior_precision = prior_precision
        prior = self.prior_precision_diag
        post = self.H + prior
        log_lik = -self.loss
        log_det_ratio = post.log().sum() - prior.log().sum()
        
        identified = self.H > 0
        scatter = (self.mean * prior * self.mean)[identified].sum()   # prior_mean = 0
        return log_lik - 0.5 * (log_det_ratio + scatter)

    def optimize_prior_precision(self, prior_structure="layerwise", init_prior_prec=1.0, n_steps=100, lr=1e-1):
        n = self.n_layers if prior_structure == "layerwise" else 1
        if isinstance(init_prior_prec, torch.Tensor):
            init = init_prior_prec.detach().reshape(-1).to(device=self.device, dtype=self.dtype)
            assert init.numel() in (1, n), f"init_prior_prec numel {init.numel()} != 1 or {n}"
            log_pp = init.log() if init.numel() == n else init.log().repeat(n)
        else:
            log_pp = torch.full((n,), float(init_prior_prec),
                                device=self.device, dtype=self.dtype).log()
        log_pp.requires_grad_(True)
        opt = torch.optim.Adam([log_pp], lr=lr)
        for _ in range(n_steps):
            opt.zero_grad()
            (-self.log_marginal_likelihood(prior_precision=log_pp.exp())).backward()
            opt.step()
        self.prior_precision = log_pp.detach().exp()


def shifted_class_labels(labels, token2class):
    ignore = labels == -100
    cls = token2class.to(labels.device)[labels.clamp(min=0)]
    cls[ignore] = -100
    return cls

def fit_diagonal_ef(model, params, fit_loader, token2class, device):
    n_params = sum(p.numel() for p in params)
    H = torch.zeros(n_params, device=device, dtype=torch.float32)
    loss_total = 0.0
    n_data = 0

    model.train()
    for i, inputs in enumerate(fit_loader):
        ids = inputs["input_ids"].to(device)
        mask = inputs["attention_mask"].to(device)
        labels = inputs["labels"].to(device)
        cls = shifted_class_labels(labels, token2class)
        shift_labels = cls[:, 1:].reshape(-1)
        if int((shift_labels != -100).sum()) == 0:
            continue  # no response tokens in this transcript

        model.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, dtype=torch.bfloat16):
            logits = model(input_ids=ids, attention_mask=mask).logits
            C = logits.size(-1)
            shift_logits = logits[:, :-1, :].reshape(-1, C)
            loss = F.cross_entropy(
                shift_logits, shift_labels, ignore_index=-100, reduction="sum"
            )
        loss.backward()

        grads = [
            (p.grad.reshape(-1) if p.grad is not None
             else torch.zeros(p.numel(), device=device, dtype=p.dtype))
            for p in params
        ]
        H += torch.cat(grads).float() ** 2
        loss_total += float(loss.item())
        n_data += 1
        if (i + 1) % 50 == 0:
            print(f"  [fit] {i + 1} transcripts, running NLL={loss_total:.1f}", flush=True)

    model.zero_grad(set_to_none=True)
    return H, loss_total, n_data


def fit_laplace_lml(model, train_unpacked, mask_collator):
    device = next(model.parameters()).device
    la = DiagLaplaceEF(model)
    params = la.params
    fit_view = train_unpacked.with_format("torch", columns=["input_ids", "attention_mask"])
    fit_loader = DataLoader(fit_view, collate_fn=mask_collator, batch_size=1)
    print(f"[laplace] fitting diagonal empirical Fisher over {la.n_params:,} "
          f"params on {len(fit_view)} transcripts ...", flush=True)
    H, loss_total, _ = fit_diagonal_ef(model, params, fit_loader, model.token2class, device)
    la.mean = parameters_to_vector(params).detach().clone()
    la.H, la.loss = H, float(loss_total)
    la.optimize_prior_precision(
        prior_structure="layerwise",
        init_prior_prec=1.0, 
        n_steps=100, 
        lr=1e-1,
    )
    lml = float(la.log_marginal_likelihood().item())
    print(f"[laplace] log marginal likelihood: {lml:.2f}", flush=True)
    model.eval()
    return lml
