# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/dentella_2023_systematic``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0); the C/N mapping is fixed.
INSTRUCTIONS = (
    "You will be shown 110 sentences in random order. For each sentence, "
    "indicate whether the sentence is grammatically correct in English. "
    "The question is always: \"Is the following sentence grammatically correct "
    "in English?\" Press C if the sentence is grammatically correct, or press N "
    "if it is not grammatically correct.\n"
)

# Verbatim stimulus material from exp0.csv (82 unique sentences across the 8
# phenomena + the 2 shared attention checks).
STIMULI = {
    "attention check": [
        ("CHECK1", "grammatical", "The new door is red"),
        ("CHECK2", "ungrammatical", "Red is new door the"),
    ],
    "Anaphora": [
        ("TS 1", "grammatical", "The new executive who oversaw the middle managers apparently doubted himself on most major decisions"),
        ("TS 2", "grammatical", "The popular sheriff who campaigned for the incumbent politicians never prepared himself for the new press briefing"),
        ("TS 3", "grammatical", "The construction worker who argued with the shift leaders undeniably hurt himself on the construction site"),
        ("TS 4", "grammatical", "The young caddy who escorted the experienced golfers supposedly dirtied himself by falling in the sand"),
        ("TS 5", "grammatical", "The police officer who aided the brilliant detectives reportedly disguised himself to get more information"),
        ("TS 6", "ungrammatical", "The football referee who argued with the large quarterbacks surprisingly excused themselves from the important game"),
        ("TS 7", "ungrammatical", "The somber minister who conversed with the religious scholars usually presented themselves as very open-minded"),
        ("TS 8", "ungrammatical", "The serious general who advised the new corporals seemingly committed themselves to the training regimen"),
        ("TS 9", "ungrammatical", "The paranoid foreman who supervised the coal miners presumably saved themselves after the awful cave-in"),
        ("TS 10", "ungrammatical", "The grimy blacksmith who worked for the royal knights evidently hurt themselves with the sharp tools"),
    ],
    "Center Embedding": [
        ("TS 1", "grammatical", "The ancient manuscript that the grad student who the new card catalog had confused a great deal was studying in the library was missing a page"),
        ("TS 2", "grammatical", "The lullaby that the famous country singer who the record label had signed to a big contract was singing yesterday was written seventy years ago"),
        ("TS 3", "grammatical", "The game that the child who the lawnmower had startled in the yard was playing in the morning lasted for hours"),
        ("TS 4", "grammatical", "The crime that the gangster who the story had profiled had planned for weeks was quickly solved"),
        ("TS 5", "grammatical", "The picture that the artist who the school had expelled for cheating was hurriedly copying was printed in a magazine"),
        ("TS 6", "ungrammatical", "The trophy that the athlete who the restaurant had hired as a spokesman was stolen later"),
        ("TS 7", "ungrammatical", "The apartment that the maid who the service had sent over was well decorated"),
        ("TS 8", "ungrammatical", "The shirt that the seamstress who the immigration officer had investigated last week needed to be dry cleaned"),
        ("TS 9", "ungrammatical", "The lecture that the professor who the newspaper story had just profiled in detail was not well attended"),
        ("TS 10", "ungrammatical", "The novel that the horror author who the publishing company had recently fired was banned by the local library"),
    ],
    "Comparative Illusion": [
        ("TS 1", "grammatical", "More gym instructors won a marathon yesterday than lawyers did"),
        ("TS 2", "grammatical", "More Americans began law school this week than Canadians did"),
        ("TS 3", "grammatical", "This month more one-year-olds took their first steps than 10-month-olds did"),
        ("TS 4", "grammatical", "Today more Brazilians immigrated to Japan than Chileans did"),
        ("TS 5", "grammatical", "More 18-year-olds voted in this election than 40-year-olds did"),
        ("TS 6", "ungrammatical", "More photographers won their third Pulitzer this year than the professor did"),
        ("TS 7", "ungrammatical", "More girls graduated from high school last year than John did"),
        ("TS 8", "ungrammatical", "This semester more foreign applicants got into Stanford than Marie did"),
        ("TS 9", "ungrammatical", "More boys got an A on the exam yesterday than she did"),
        ("TS 10", "ungrammatical", "Last month more couples had their second child than Sandra's sister did"),
    ],
    "Intrusive Resumption": [
        ("TS 1", "grammatical", "This is the boy that the cop who was leading the operation beat up"),
        ("TS 2", "grammatical", "This is the girl that the child who was playing with the doll loved"),
        ("TS 3", "grammatical", "This is the boy that the teachers who were teaching mathematics praised"),
        ("TS 4", "grammatical", "These are the flowers that the gardener who was working on John's flowerbed planted"),
        ("TS 5", "grammatical", "These are the cakes that the pastry chefs who were participating in the competition baked"),
        ("TS 6", "ungrammatical", "This is the girl that the boy who was working with the gardener courted her"),
        ("TS 7", "ungrammatical", "This is the actress that the judge who was working at Cannes admired her"),
        ("TS 8", "ungrammatical", "This is the mug that the artisans who were working with ceramics crafted it"),
        ("TS 9", "ungrammatical", "This is the dictionary entry that the students who were doing the exam looked it up"),
        ("TS 10", "ungrammatical", "This is the competition that the athletes who were feeling tired gave it up"),
    ],
    "NPIs": [
        ("TS 1", "grammatical", "No authors that the critics recommended have received any acknowledgment for a best-selling novel"),
        ("TS 2", "grammatical", "No ambassadors that the diplomats consulted have ever seen brutality in the foreign war"),
        ("TS 3", "grammatical", "No customers that the salesmen assisted have expressed any optimism for a full refund"),
        ("TS 4", "grammatical", "No detergents that the housewives used have ever caused damage to the delicate clothing"),
        ("TS 5", "grammatical", "No students that the teachers punished could expect any friendliness from the strict principal"),
        ("TS 6", "ungrammatical", "The soldiers that no diplomats supported have shown any bravery in the controversial war"),
        ("TS 7", "ungrammatical", "The professors that no students respected have ever wanted negativity in a class debate"),
        ("TS 8", "ungrammatical", "The comments that no politicians ignored have caused any bitterness toward the liberal newspapers"),
        ("TS 9", "ungrammatical", "The lawyers that no businessmen respected have ever received criticism for a bad trial"),
        ("TS 10", "ungrammatical", "The babysitters that no children obeyed have shown any gratitude to the disappointed parents"),
    ],
    "Order of Adjectives": [
        ("TS 1", "grammatical", "I wore a beautiful long Italian silk dress"),
        ("TS 2", "grammatical", "I bought a nice small German electric bike"),
        ("TS 3", "grammatical", "I washed an ugly wide American wool sweater"),
        ("TS 4", "grammatical", "I painted a fine short Swedish wooden table"),
        ("TS 5", "grammatical", "I saw a graceful tall Venetian vitreous vase"),
        ("TS 6", "ungrammatical", "I wore a silk Italian long beautiful dress"),
        ("TS 7", "ungrammatical", "I bought an electric German small nice bike"),
        ("TS 8", "ungrammatical", "I washed a wool American wide ugly sweater"),
        ("TS 9", "ungrammatical", "I painted a wooden Swedish short fine table"),
        ("TS 10", "ungrammatical", "I saw a vitreous Venetian tall graceful vase"),
    ],
    "Order of Adverbs": [
        ("TS 1", "grammatical", "Charlotte allegedly once was an acrobat"),
        ("TS 2", "grammatical", "Sean probably already did his homework"),
        ("TS 3", "grammatical", "Melissa then always cleaned the dishes"),
        ("TS 4", "grammatical", "Dre perhaps still takes dance lessons"),
        ("TS 5", "grammatical", "Emily probably no longer drinks beer"),
        ("TS 6", "ungrammatical", "Marc once allegedly was a firefighter"),
        ("TS 7", "ungrammatical", "Sonja already probably set the table"),
        ("TS 8", "ungrammatical", "Jacob always then did his homework"),
        ("TS 9", "ungrammatical", "Gary still perhaps drives to work"),
        ("TS 10", "ungrammatical", "Jeff no longer probably eats sushi"),
    ],
    "Plural Attraction": [
        ("TS 1", "grammatical", "The key to the cabinets probably was destroyed by the fire"),
        ("TS 2", "grammatical", "The picture on the fliers definitely was of a village church in the south of France"),
        ("TS 3", "grammatical", "The label on the containers probably was a warning about the hazardous chemicals inside"),
        ("TS 4", "grammatical", "The crime in the suburbs doubtlessly was a reflection of the violence in today's society"),
        ("TS 5", "grammatical", "The entrance to the exhibits evidently was hard to locate on the diagram"),
        ("TS 6", "ungrammatical", "The slogan on the posters unsurprisingly were designed to get attention"),
        ("TS 7", "ungrammatical", "The mistake in the programs certainly were disastrous for the small software company"),
        ("TS 8", "ungrammatical", "The problem in the stores ultimately were solved by firing the custodian"),
        ("TS 9", "ungrammatical", "The defect in the appliances likely were unknown to consumers and government regulators"),
        ("TS 10", "ungrammatical", "The door to the laboratories accidentally were left unlocked by the cleaning service"),
    ],
}

PHENOMENA = ["Anaphora", "Center Embedding", "Comparative Illusion",
             "Intrusive Resumption", "NPIs", "Order of Adjectives",
             "Order of Adverbs", "Plural Attraction"]


class GrammaticalityJudgment:
    """Grammaticality-judgment experiment, Dentella, Günther, & Leivada (2023),
    "Systematic testing of three Language Models reveals low language accuracy,
    absence of response stability, and a yes-response bias", PNAS 120(51).

    Design (Human Data / Methods, p. 2): each participant is assigned one of 8
    counterbalanced lists = one of 8 linguistic phenomena. Each phenomenon
    contributes 10 sentences (5 grammatical, 5 ungrammatical), each judged 10
    times, plus 2 attention-check sentences (1 grammatical, 1 ungrammatical)
    each judged 5 times -> 100 + 10 = 110 trials presented in random order.
    On each trial the participant presses C (grammatical) or N (not).

    ASSUMPTION: each simulated participant draws one of the 8 phenomena
    uniformly at random, and the 110 presentations (10 items x10 + 2 checks
    x5) are shuffled uniformly. The correct/stability codings follow the data:
    stability is NaN on the first presentation of a sentence and otherwise 1.0
    if the judgment changed from the previous presentation of the same item,
    else 0.0. The C/N token mapping is fixed (C = grammatical, N = not), as in
    the transcripts.

    The DataFrame matches exp0.csv minus the demographic columns (gender, age,
    language, speech_therapy, mental_conditions), which a text simulator cannot
    produce.
    """

    def __init__(self):
        self.name = "dentella_2023_systematic_exp0"
        self.checks_per_item = 5
        self.test_reps = 10
        self.choices = ["C", "N"]

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            phenomenon = PHENOMENA[int(np.random.randint(0, len(PHENOMENA)))]
            trials = []
            for item, cond, sentence in STIMULI["attention check"]:
                trials.append((item, "attention check", cond, sentence, self.checks_per_item))
            for item, cond, sentence in STIMULI[phenomenon]:
                trials.append((item, phenomenon, cond, sentence, self.test_reps))
            expanded = []
            for item, phen, cond, sentence, reps in trials:
                expanded.extend([(item, phen, cond, sentence)] * reps)
            order = list(range(len(expanded)))
            np.random.shuffle(order)
            prompt = INSTRUCTIONS
            seen_count, prev_response = {}, {}
            trial = 0
            for trial_index in order:
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                item, phen, cond, sentence = expanded[trial_index]
                repetition = seen_count.get(item, 0) + 1
                seen_count[item] = repetition
                prompt += f"Sentence: \"{sentence}\". You press [HUMAN_RESPONSE]"
                letter = agent(prompt, choice_options=self.choices)
                prompt += f"{letter}[/HUMAN_RESPONSE].\n"
                response = 1 if letter == "C" else 0
                correct = int((response == 1) == (cond == "grammatical"))
                stability = np.nan
                if item in prev_response:
                    stability = 1.0 if response != prev_response[item] else 0.0
                prev_response[item] = response
                rows.append({
                    "participant_id": participant, "trial": trial,
                    "response": response, "sentence": sentence,
                    "test_item": item, "phenomenon": phen,
                    "condition": cond, "correct": correct,
                    "repetition": repetition, "stability": stability,
                })
                trial += 1
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "sentence", "test_item",
            "phenomenon", "condition", "correct", "repetition", "stability",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3, help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None, help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None, help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = GrammaticalityJudgment()
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