# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp5 (Study 5) of ``Hugging-Brain/gunadi_2022_impact``,
format-identical to the repo's ``transcripts5.jsonl``.

``uv run simulate5.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import math

import numpy as np
import pandas as pd
from tqdm import tqdm

# Four real products, each with a 2(direction) x 2(frequency) price manipulation
# (paper Study 5, "Procedure", pp. 27-29; Table 2). Product metadata, prices,
# and labels are verbatim from build_jsonl.py's EXP5_PRODUCTS / EXP5_LABELS.
PRODUCTS = {
    "card_holder": {
        "label": "card holder", "title": "Aluminum Card Holder with Leather Case",
        "desc": "Maximum capacity of 8 standard-sized cards. Made with soft and durable "
                "leather. Minimalist and slim design, extremely light and convenient to "
                "carry.",
        "current": 15,
        "prices": {"dec_single": [24, 24, 24, 24], "dec_multiple": [24, 22, 19, 17],
                   "inc_single": [6, 6, 6, 6], "inc_multiple": [6, 8, 11, 13]}},
    "charger": {
        "label": "battery charger", "title": "Portable Battery Charger",
        "desc": "External portable battery charger with 2,200 mAh capacity. Very light, "
                "aluminum finished body, with an extra-flat design. Has both MicroUSB and "
                "USB-C inputs.",
        "current": 15,
        "prices": {"dec_single": [23, 23, 23, 23], "dec_multiple": [23, 21, 20, 17],
                   "inc_single": [7, 7, 7, 7], "inc_multiple": [7, 9, 10, 13]}},
    "water_bottle": {
        "label": "water bottle", "title": "Reusable Water Bottle",
        "desc": "",
        "current": 10,
        "prices": {"dec_single": [16, 16, 16, 16], "dec_multiple": [16, 15, 13, 12],
                   "inc_single": [4, 4, 4, 4], "inc_multiple": [4, 5, 7, 8]}},
    "laptop_bag": {
        "label": "laptop bag", "title": "Laptop Bag with Adjustable Straps",
        "desc": "This light laptop bag comes with an adjustable strap and two front "
                "pockets. Inside, it has a padded compartment for a laptop up to 13.3 "
                "inches in size.",
        "current": 20,
        "prices": {"dec_single": [30, 30, 30, 30], "dec_multiple": [30, 28, 25, 22],
                   "inc_single": [10, 10, 10, 10], "inc_multiple": [10, 12, 15, 18]}},
}
LABELS = ["4 days ago", "3 days ago", "2 days ago", "1 day ago"]
PROD_VAR = {"card_holder": "Card", "charger": "Charger",
            "water_bottle": "Bot", "laptop_bag": "Bag"}
COND_VAR = {"dec_single": "DecLo", "dec_multiple": "DecHi",
            "inc_single": "IncLo", "inc_multiple": "IncHi"}
CONDITIONS = list(COND_VAR.keys())
PRODUCT_ORDER = list(PRODUCTS.keys())
FILLERS = [("How much did you like the look of the pages?", "q77_look"),
           ("How likely would you be to purchase there?", "q78_purchase_likely"),
           ("How likely would you be to recommend the platform?", "q79_recommend_likely"),
           ("Does the look fit the brand/image?", "q81_brand_fit")]
FILLER_COLS = [c for _, c in FILLERS]


def _eur(price):
    f = float(price)
    return "€" + (str(int(f)) if f.is_integer() else f"{f:.2f}")


class StoreDeferral:
    """Consequential purchase-deferral task, Study 5 of Gunadi & Evangelidis
    (2022), "The impact of historical price information on purchase deferral",
    Journal of Marketing Research, 59(3), 623-640.

    Design (Study 5, Procedure, pp. 27-29): a student reviews four university
    store products, each with its own randomly assigned 2(direction) x
    2(frequency) price condition. On each product the student chooses to buy now
    (response 0, token N) or wait (response 1, token W); when waiting they may
    opt in to an email price update (token Y / value 4) or not (token N / value
    5). A free-text rationale and then four 1-7 filler ratings follow.

    ASSUMPTION: each product's condition is drawn uniformly at random per trial
    (the raw CSV has no assignment rule). The paper says products appeared in
    random order; the CSV and build_jsonl use the fixed order card_holder,
    charger, water_bottle, laptop_bag (matching the ``trial`` index), which this
    simulator mirrors. ``update_optin`` is NaN when the buyer buys now and 4 (Y)
    or 5 (N) otherwise, as in the CSV. All other text is verbatim from
    build_jsonl.py's transcribe_exp5.

    The DataFrame matches exp5.csv minus the demographic columns ``age`` and
    ``gender``.
    """

    def __init__(self):
        self.name = "gunadi_2022_impact_exp5"
        self.conditions = CONDITIONS
        self.products = PRODUCTS
        self.labels = LABELS
        self.product_order = PRODUCT_ORDER

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            prompt = ("You are testing a new online platform for the university store, "
                      "which sells university-branded products and uses dynamic pricing "
                      "(like Amazon), so prices may change frequently. You will review 4 "
                      "products. On each product page, you decide whether to buy now or "
                      "wait. If you wait, you may receive a later price update. Your "
                      "decisions are consequential: after the study a random draw selects "
                      "5 participants, and your choices are carried out with €20 funded by "
                      "the study.\n"
                      "On each product, press N to buy now, or W to wait to buy. If you "
                      "wait on a product, you are later asked whether you want to receive "
                      "a price update by email: press Y for yes or N for no.")
            product_rows = {}
            for trial, product in enumerate(self.product_order):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                meta = self.products[product]
                cond = str(np.random.choice(self.conditions))
                prices = meta["prices"][cond]
                history = " | ".join(f"Was {_eur(p)} ({l})"
                                     for p, l in zip(prices, self.labels))
                desc = meta.get("desc") or "A university-branded product."
                prompt += (f"\nProduct: {meta['title']}. {desc} "
                           f"Price history: {history}. CURRENT PRICE: "
                           f"{_eur(meta['current'])}. What will you do? "
                           "You press [HUMAN_RESPONSE]")
                token = agent(prompt, choice_options=["N", "W"])
                prompt += f"{token}[/HUMAN_RESPONSE]."
                response = 0 if token == "N" else 1
                optin = np.nan
                if response == 1:
                    prompt += (" You are asked whether you want to receive a price update "
                               f"for the {meta['label']} by email. You press "
                               "[HUMAN_RESPONSE]")
                    otoken = agent(prompt, choice_options=["Y", "N"])
                    prompt += f"{otoken}[/HUMAN_RESPONSE]."
                    optin = 4.0 if otoken == "Y" else 5.0
                product_rows[product] = {
                    "trial": trial, "response": response, "optin": optin,
                    "variable": f"S{PROD_VAR[product]}{COND_VAR[cond]}",
                    "condition": cond, "product": product,
                }
            prompt += "\nYou briefly explain what motivated your decisions: [HUMAN_RESPONSE]"
            why = agent(prompt, choice_options=None)
            prompt += f"{why}[/HUMAN_RESPONSE]."
            filler_vals = []
            for q, _ in FILLERS:
                prompt += (f"\n'{q}' (1 = not at all, 7 = very much). "
                           "You rate [HUMAN_RESPONSE]")
                ft = agent(prompt, choice_options=["1", "2", "3", "4", "5", "6", "7"])
                prompt += f"{ft}[/HUMAN_RESPONSE]."
                filler_vals.append(float(ft))
            for product, r in product_rows.items():
                rows.append({
                    "participant_id": f"P{participant:03d}", "trial": r["trial"],
                    "response": r["response"], "variable": r["variable"],
                    "condition": r["condition"], "product": r["product"],
                    "update_optin": r["optin"], "why": why,
                    "q77_look": filler_vals[0], "q78_purchase_likely": filler_vals[1],
                    "q79_recommend_likely": filler_vals[2], "q81_brand_fit": filler_vals[3],
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "variable", "condition", "product",
            "update_optin", "why", "q77_look", "q78_purchase_likely",
            "q79_recommend_likely", "q81_brand_fit",
        ])
        return df, prompts


def _random_agent(prompt, choice_options=None):
    if choice_options is None:
        return "I assumed the price would keep following the same pattern as before."
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3, help="number of simulations (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None, help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None, help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = StoreDeferral()
    df, prompts = task.simulate(_random_agent, args.num_simulations,
                                max_chars=args.max_chars)

    print(f"name: {task.name}")
    print(f"df shape: {df.shape}")
    print("dtypes:")
    print(df.dtypes.to_string())
    print("head:")
    print(df.head(8).to_string())
    print(f"prompt lengths: {[len(p) for p in prompts]}")
    for i, p in enumerate(prompts):
        first = p.splitlines()[0]
        if len(first) > 180:
            first = first[:90] + " … " + first[-90:]
        print(f"participant {i} first line: {first}")
    print("=" * 78)
    print("first prompt, head:")
    print(prompts[0][:600])
    print("...")
    print("first prompt, tail:")
    print(prompts[0][-300:])


if __name__ == "__main__":
    main()