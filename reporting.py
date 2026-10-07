import json
import os


def write_train_report(*, run_name, output_dir, model, results, lml, trainer):
    nll_train = sum(nll for nll, _ in results["train"].values())
    n_train = sum(n for _, n in results["train"].values())
    nll_test = sum(nll for nll, _ in results["test"].values())
    n_test = sum(n for _, n in results["test"].values())

    for split_name in ("train", "test"):
        print(f"\n=== final eval: {split_name} ===")
        print(f"{'study':<40} {'n_tokens':>10} {'nll':>14} {'mean':>8}")
        for study, (nll, n) in sorted(results[split_name].items()):
            mean = nll / n if n else float("nan")
            print(f"{study:<40} {n:>10} {nll:>14.4f} {mean:>8.4f}")
        total_nll = nll_train if split_name == "train" else nll_test
        total_n = n_train if split_name == "train" else n_test
        mean = total_nll / total_n if total_n else float("nan")
        print(f"{'TOTAL':<40} {total_n:>10} {total_nll:>14.4f} {mean:>8.4f}")

    print(f"log marginal likelihood (Laplace): {lml:.4f}")

    report = {
        "log_marginal_likelihood": lml,
        "nll": {
            split_name: {
                "total": sum(nll for nll, _ in results[split_name].values()),
                "n_tokens": sum(n for _, n in results[split_name].values()),
                "per_study": {
                    study: {"nll": nll, "n_tokens": n, "mean": (nll / n if n else None)}
                    for study, (nll, n) in sorted(results[split_name].items())
                },
            }
            for split_name in results
        },
    }
    with open(os.path.join(output_dir, "final_eval.json"), "w") as f:
        json.dump(report, f, indent=2)

    os.makedirs("results_reports", exist_ok=True)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    md = [
        f"# {run_name}",
        "",
        f"- output_dir: `{output_dir}`",
        f"- parameters: {total_params:,} total, {trainable_params:,} trainable",
        f"- log marginal likelihood (Laplace, all-weights diagonal "
        f"empirical Fisher): {lml:.4f}",
    ]

    def md_cells(split_name, study):
        entry = results[split_name].get(study)
        if entry is None:
            return ["-", "-", "-"]
        nll, n = entry
        mean = nll / n if n else float("nan")
        return [str(n), f"{nll:.4f}", f"{mean:.4f}"]

    md += [
        "",
        "## NLL",
        "",
        "| study | n (train) | nll (train) | mean (train) | n (test) | nll (test) | mean (test) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for study in sorted(set(results["train"]) | set(results["test"])):
        md.append("| " + " | ".join([study] + md_cells("train", study) + md_cells("test", study)) + " |")
    train_mean = nll_train / n_train if n_train else float("nan")
    test_mean = nll_test / n_test if n_test else float("nan")
    md.append(
        f"| **TOTAL** | {n_train} | {nll_train:.4f} | {train_mean:.4f} "
        f"| {n_test} | {nll_test:.4f} | {test_mean:.4f} |"
    )

    def fmt_num(v, fmt="{:.4f}"):
        return fmt.format(v) if isinstance(v, (int, float)) else "-"

    eval_logs = [h for h in trainer.state.log_history if "eval_loss" in h]
    train_logs = [h for h in trainer.state.log_history if "loss" in h]
    runtime = next((h for h in trainer.state.log_history if "train_runtime" in h), None)
    md += ["", "## Training log", ""]
    if runtime is not None:
        md += [f"- train_runtime: {fmt_num(runtime.get('train_runtime'), '{:.0f}')}s, "
               f"avg train_loss: {fmt_num(runtime.get('train_loss'))}", ""]
    if eval_logs:
        md += ["Eval loss:", "", "| step | epoch | eval_loss |", "|---:|---:|---:|"]
        for h in eval_logs:
            md.append(f"| {h.get('step', '-')} | {fmt_num(h.get('epoch'), '{:.2f}')} "
                      f"| {fmt_num(h.get('eval_loss'))} |")
        md.append("")
    if train_logs:
        def train_row(h):
            return (f"| {h.get('step', '-')} | {fmt_num(h.get('epoch'), '{:.2f}')} "
                    f"| {fmt_num(h.get('loss'))} | {fmt_num(h.get('grad_norm'), '{:.2f}')} "
                    f"| {fmt_num(h.get('learning_rate'), '{:.2e}')} |")

        table_header = ["| step | epoch | loss | grad_norm | lr |",
                        "|---:|---:|---:|---:|---:|"]
        stride = max(1, -(-len(train_logs) // 100))
        sampled = train_logs[::stride]
        if sampled[-1] is not train_logs[-1]:
            sampled.append(train_logs[-1])
        note = f" (every {stride}th of {len(train_logs)} logged steps)" if stride > 1 else ""
        md += [f"Train loss{note}:", ""] + table_header
        md += [train_row(h) for h in sampled]

        if stride > 1:
            md += ["", "<details>",
                   f"<summary>Full train loss log ({len(train_logs)} logged steps)</summary>", ""]
            md += table_header
            md += [train_row(h) for h in train_logs]
            md += ["", "</details>"]

    md += ["", "## Architecture", "", "```", str(model), "```", ""]
    md_path = os.path.join("results_reports", run_name + ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Wrote report to {md_path}")
