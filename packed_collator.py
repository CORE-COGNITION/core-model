from typing import Dict, List

import torch
from torch.utils.data import IterableDataset
from trl import DataCollatorForCompletionOnlyLM

class PackedIterableDataset(IterableDataset):
    """Streams already-packed rows from a tokenized map-style dataset.
    Each yielded item is one pack ready for the model: input_ids (T_flat,),
    labels (T_flat,), cu_seqlens (n_segs+1,). 
    """

    def __init__(
        self,
        base_dataset,
        tokenizer,
        response_template,
        instruction_template,
        target_tokens: int,
        pad_to_multiple_of: int = 64,
        shuffle: bool = True,
        seed: int = 0,
    ):
        self.base = base_dataset
        self.target_tokens = target_tokens
        self.pad_to_multiple_of = pad_to_multiple_of
        self.pad_id = tokenizer.pad_token_id
        self._mask = DataCollatorForCompletionOnlyLM(
            response_template=response_template,
            instruction_template=instruction_template,
            tokenizer=tokenizer,
        )
        self.shuffle = shuffle
        self.seed = seed
        self._call_count = 0
        self._cached_len = None

    def _per_example_labels(self, ids: List[int]) -> List[int]:
        out = self._mask([{"input_ids": ids}])["labels"][0].tolist()
        return out[: len(ids)]

    def _finalize(self, all_ids, all_labels, cu) -> Dict[str, torch.Tensor]:
        pad = (-len(all_ids)) % self.pad_to_multiple_of
        if pad:
            all_ids = all_ids + [self.pad_id] * pad
            all_labels = all_labels + [-100] * pad
            cu = cu + [len(all_ids)]
        return {
            "input_ids": torch.tensor(all_ids, dtype=torch.long),
            "labels": torch.tensor(all_labels, dtype=torch.long),
            "cu_seqlens": torch.tensor(cu, dtype=torch.int32),
        }

    def __iter__(self):
        worker_info = torch.utils.data.get_worker_info()
        n_workers = worker_info.num_workers if worker_info else 1
        worker_id = worker_info.id if worker_info else 0

        n = len(self.base)
        if self.shuffle:
            rng = torch.Generator().manual_seed(self.seed + self._call_count)
            order = torch.randperm(n, generator=rng).tolist()
        else:
            order = list(range(n))
        self._call_count += 1
        order = order[worker_id::n_workers]

        all_ids: List[int] = []
        all_labels: List[int] = []
        cu: List[int] = [0]

        for idx in order:
            ids = list(self.base[int(idx)]["input_ids"])
            if len(ids) > self.target_tokens:
                ids = ids[: self.target_tokens]
            if all_ids and len(all_ids) + len(ids) > self.target_tokens:
                yield self._finalize(all_ids, all_labels, cu)
                all_ids, all_labels, cu = [], [], [0]
            all_ids.extend(ids)
            all_labels.extend(self._per_example_labels(ids))
            cu.append(len(all_ids))

        if all_ids:
            yield self._finalize(all_ids, all_labels, cu)

    def __len__(self):
        if self._cached_len is not None:
            return self._cached_len
        total = 0
        for row in self.base:
            total += min(len(row["input_ids"]), self.target_tokens)

        self._cached_len = max(1, -(-total // self.target_tokens) + 4)
        return self._cached_len


def pack_passthrough_collator(features):
    f = features[0]
    return {
        "input_ids": f["input_ids"].unsqueeze(0),
        "labels": f["labels"].unsqueeze(0),
        "cu_seqlens": f["cu_seqlens"],
    }
