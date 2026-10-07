# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/jansen_2021_rational`` (Grammar
study, Study 1 of Jansen, Rafferty & Griffiths, 2021), format-identical to the
repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import random as _rnd

import numpy as np
import pandas as pd
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Verbatim from build_jsonl.py: the narration template + question bank.
# ---------------------------------------------------------------------------
EXP0_ATT1 = ["Grammar", "Logical reasoning", "Creative writing"]
EXP0_ATT2 = ["It will be underlined", "It will be deleted", "It will be all caps"]

LETTERS = "ABCDE"

EXP0_BANK = {
    'Q1': {"stem": 'The school-age child faces a formidable task when during the first few years of classroom experiences ["he or she is expected to master the printed form of language"].', "choices": ['he or she is expected to master the printed form of language.', 'he or she expects to master the printed form of language.', 'he or she faces expectations of mastering the printed form of language.', 'mastery of the printed form of language is expected of him or her.', 'mastery of print is expected by his or her teacher.']},
    'Q2': {"stem": 'He came to the United States as a young ["man, he found"] a job as a coal miner.', "choices": ['man, he found', 'man and found', 'man and there he was able to find', 'man and then finding', 'man and had found']},
    'Q3': {"stem": 'To a large degree, ["poetry, along with all the other arts, is"] a form of imitation.', "choices": ['poetry, along with all the other arts, is', 'poetry along with all the other arts is', 'poetry, along with all the other arts, are', 'poetry, and other arts, is', 'poetry and art are']},
    'Q4': {"stem": 'Delegates to the political convention found ["difficulty to choose"] a candidate from among the few nominated.', "choices": ['difficulty to choose', 'it difficult in making the choice of', 'it difficult to choose', 'choosing difficult when selecting', 'making a choice difficult in selecting']},
    'Q5': {"stem": 'Reading in any language can be viewed as a developmental task much the same as learning to walk, to cross the street independently, to care for one\'s possessions, or ["accepting responsibility for one\'s own decisions."]', "choices": ["accepting responsibility for one's own decisions.", "accepting one's own decisions responsibly.", "to accept responsibility for one's own decisions.", "accepting responsibility and making one's own decisions.", "to make one's own decisions."]},
    'Q6': {"stem": 'Sea forests of giant kelp, which fringe only one coastline in the Northern Hemisphere, ["is native to shores"] throughout the Southern Hemisphere.', "choices": ['is native to shores', 'is native to most shores', 'are native only in shores', 'are native', 'are native to shores']},
    'Q7': {"stem": 'Taking an occasional respite between chapters or assignments is more desirable ["than a long, continuous period of study."]', "choices": ['than a long, continuous period of study.', 'than a period of long, continuous study.', 'than a long period of continuous study.', 'than studying for a long, continuous period.', 'than a study period long and continuous.']},
    'Q8': {"stem": 'Like so many characters in Russian fiction, ["Crime and Punishment exhibits"] a behavior so foreign to the American temperament that many readers find the story rather incredible.', "choices": ['Crime and Punishment exhibits', 'those in Crime and Punishment exhibit', 'those in Crime and Punishment exhibits', 'often exhibiting', 'characterized by']},
    'Q9': {"stem": 'Don Quixote provides a cross section of Spanish life, thought, and ["portrays the feelings of many Spaniards"] at the end of the chivalric age.', "choices": ['portrays the feelings of many Spaniards', 'portrayal of the feelings of many Spaniards', 'feelings portrayed by Spaniards', 'feelings', 'Spanish feelings']},
    'Q10': {"stem": 'Hamlet, Prince of Denmark thought several times of killing Claudius ["and finally succeeding"] in doing so.', "choices": ['and finally succeeding', 'that finally was successful', 'finally a successful attempt', 'being finally successful', 'and finally succeeded']},
    'Q11': {"stem": 'The lamb ["had laid on the hay beside its mother and had begun to nurse as soon as the boy had sat"] the lantern on the table.', "choices": ['had laid on the hay beside its mother and had begun to nurse as soon as the boy had sat', 'had lain on the hay beside its mother and had begun to nurse as soon as the boy had set', 'had laid on the hay beside its mother and had begun to nurse as soon as the boy had set', 'had lain on the hay besides its mother and had begun to nurse as soon as the boy had set', "had lain on the hay beside it's mother and had begun to nurse as soon as the boy had set"]},
    'Q12': {"stem": 'An infant, ["whether lying alone in the crib or enjoying the company of adults, is consistently fascinated at"] the movement of toes and fingers.', "choices": ['whether lying alone in the crib or enjoying the company of adults, is consistently fascinated at', 'alone or in company, is consistently fascinated at', 'whether lying alone in the crib or enjoying the company of adults, is constantly fascinated at', 'whether lying alone in the crib or enjoying the company of adults, is consistently fascinated by', 'lonely in the crib and enjoying the company of adults is consistently fascinated at']},
    'Q13': {"stem": 'A policeman of proven valor, ["the city council designated him"] the "Outstanding Law Enforcement Officer of the Year."', "choices": ['the city council designated him', "the city council's designating him", 'the city council will designate him', 'he designated the city council', 'he was designated by the city council']},
    'Q14': {"stem": 'The supervisor asked, [""Bob have you checked with our office in Canton, Ohio, to see if it stocks slate, flagstone, and feather rock?""]', "choices": ['"Bob have you checked with our office in Canton, Ohio, to see if it stocks slate, flagstone, and feather rock?"', '"Bob, have you checked with our office in Canton, Ohio to see if it stocks slate, flagstone, and feather rock?"', '"Bob, have you checked with our office in Canton, Ohio, to see if it stocks slate, flagstone, and feather rock?"', 'Bob, have you checked with our office in Canton, Ohio, to see if it stocks slate, flagstone, and feather rock?', '"Bob have you checked with our office in Canton, Ohio, to see if it stocks slate flagstone and feather rock?"']},
    'Q15': {"stem": '["If the room would have been brighter"], I would have been more successful in my search for the lost earrings.', "choices": ['If the room would have been brighter', 'If rooms were brighter', 'If the room could have been brighter', 'If the room had been brighter', 'If the room was brighter']},
    'Q16': {"stem": 'After announcing that no notes could be used during the final exam, the instructor was compelled to fail ["two students because they used notes anyway."]', "choices": ['two students because they used notes anyway.', 'two students because of their notes.', 'two students because of them using notes.', 'two students whose notes were used.', 'two students due to the use of their notes.']},
    'Q17': {"stem": 'The respiratory membranes, ["through which exchange of gases occurs"], are the linings of the lungs.', "choices": ['through which exchange of gases occurs', 'through which exchange of gas occurs', 'after gases are exchanged', 'occurs through the exchange of gases', 'through which gas is exchanged']},
    'Q18': {"stem": 'Jeff is one of those ["who tends to resist any attempt at"] classification or regulation.', "choices": ['who tends to resist any attempt at', 'whose tendency to resist any attempt at', 'who tend to resist any attempt at', 'who tends to resist any attempt to', 'who tends to resistance of any attempt at']},
    'Q19': {"stem": '["The amount of water in living cells vary"], but it is usually 65 percent and in some organisms may be as high as 96 percent or more of the total substance.', "choices": ['The amount of water in living cells vary', 'The amount of water varies', 'The amount of water in cells vary', 'The amount of water in living cells varies', 'The amounts of water varies in living cells']},
    'Q20': {"stem": '["The belief of ancient scientists was"] that maggots are generated from decaying bodies and filth and are not formed by reproduction.', "choices": ['The belief of ancient scientists was', 'The ancient scientists beliefs were', 'The ancient scientists believe', 'The belief of ancient scientists were', 'The ancient belief of scientists was']},
}

QIDS = [f"Q{i}" for i in range(1, 21)]

# Pre-test self-assessment specs: (column, narration question, min value, max value).
PRE_ASSESS = [
    ("grammarAssess0_1",
     "Compared to other participants in this study, how would you rate  your overall ability "
     "to recognize correct grammar? (a number from 0 to 100)", 0, 100),
    ("absAssess0", "How many of the 20 questions do you think you will answer correctly? (a number from 0 to 20)", 0, 20),
    ("relAssess0_1", "Compared to other participants in this study, how well do you think you will do? (a number from 0 to 100)", 0, 100),
    ("diffSelf0_1", "How difficult is recognizing correct grammar for you? (1 = very easy, 10 = very difficult)", 1, 10),
    ("diffOther0_1", "How difficult is recognizing correct grammar for the average participant? (1 = very easy, 10 = very difficult)", 1, 10),
]

POST_ASSESS = [
    ("grammarAssess1_1",
     "Compared to other participants in this study, how would you rate  your overall ability "
     "to recognize correct grammar? (a number from 0 to 100)", 0, 100),
    ("absAssess1", "How many of the 20 grammar questions you just completed do you think you answered correctly? (a number from 0 to 20)", 0, 20),
    ("relAssess1_1", "Compared to other participants in this study, how well do you think you performed? (a number from 0 to 100)", 0, 100),
    ("diffSelf1_1", "How difficult was recognizing correct grammar for you? (1 = very easy, 10 = very difficult)", 1, 10),
    ("diffOther1_1", "How difficult was recognizing correct grammar for the average participant? (1 = very easy, 10 = very difficult)", 1, 10),
]


def _seed_int(seed):
    try:
        return int(float(seed))
    except (TypeError, ValueError):
        return 0


def _shuffle(seed, n):
    order = list(range(n))
    _rnd.Random(_seed_int(seed)).shuffle(order)
    return order


class GrammarSelfAssessment:
    """Grammar study (Study 1) of Jansen, Rafferty & Griffiths (2021), "A
    rational model of the Dunning-Kruger effect supports insensitivity to
    evidence in low performers", Nature Human Behaviour 5, 756-763.

    Session structure (Study 1, Methods/Procedure; recovered from the shipped
    transcripts and build_jsonl.py because the article body is paywalled at
    nature.com): consent + instructions; two fixed-order comprehension checks
    (subject, underlining); five pre-test self-assessments (0-100 relative
    ability, 0-20 absolute count, 0-100 relative performance, two 1-10
    difficulty scales); 20 multiple-choice grammar rephrasing items each with 5
    choices; five post-test self-assessments; demographics note.

    The participant's 20 answers are chosen freely by the agent among the 5
    shuffled options; the five self-assessment values are drawn by the agent
    uniformly over each item's integer scale. Option lettering for the 20 items
    is shuffled per participant from the stored ``random`` seed exactly as
    build_jsonl.py does, so the round trip is byte-identical.

    The DataFrame matches exp0.csv minus demographic/timing columns (age,
    gender, race, education, StartDate, etc.) that a text simulator cannot
    produce.

    ASSUMPTION: The article Methods is paywalled, so the design is taken from
    the shipped transcripts/build_jsonl.py; the structure (20 items + pre/post
    self-assessment) is unambiguous there.
    ASSUMPTION: No answer key is stored in the data, so correctness is not
    modeled -- the agent freely picks any of the 5 options (format identity,
    not accuracy, is the contract).
    ASSUMPTION: Comprehension-check and self-assessment free responses are
    drawn by the agent uniformly over their valid range; comprehension-check
    letters are fixed (A,B,C) exactly as in build_jsonl.py.
    """

    def __init__(self):
        self.name = "jansen_2021_rational_exp0"
        self.num_questions = 20

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = f"SIM{participant:05d}"
            seed = int(np.random.randint(100000, 999999))

            prompt = ("You are taking part in a study on how people perceive their own abilities. "
                      "You first read an informed-consent statement and then decide to continue. "
                      "The task instructions say: 'In this task, you're going to be answering a set of 20 questions "
                      "about grammar. In each question, some part of each sentence is underlined; sometimes the whole "
                      "sentence is underlined. Five choices for rephrasing the underlined part follow each sentence; "
                      "one choice repeats the original, and the other four are different. For each sentence, consider "
                      "the requirements of standard written English. Your choice should be a correct and effective "
                      "expression, not awkward or ambiguous. Focus on grammar, sentence structure, punctuation, "
                      "wordiness, and word choice. If a choice changes the meaning of the original sentence, do not "
                      "select it.' On every question you press the letter of the option you choose (A, B, C, ...).")

            # Comprehension check 1
            prompt += (" First you must pass a short comprehension test. Question: 'What subject are you going to be "
                       "answering questions about?' Options: ")
            prompt += " ".join(LETTERS[i] + ") " + o for i, o in enumerate(EXP0_ATT1))
            prompt += " You press [HUMAN_RESPONSE]"
            l1 = agent(prompt, ["A", "B", "C"])
            prompt += f"{l1}[/HUMAN_RESPONSE]."
            att1 = EXP0_ATT1["ABC".index(l1)]

            # Comprehension check 2
            prompt += " Question: 'What will be done to a part of each sentence?' Options: "
            prompt += " ".join(LETTERS[i] + ") " + o for i, o in enumerate(EXP0_ATT2))
            prompt += " You press [HUMAN_RESPONSE]"
            l2 = agent(prompt, ["A", "B", "C"])
            prompt += f"{l2}[/HUMAN_RESPONSE]."
            att2 = EXP0_ATT2["ABC".index(l2)]

            prompt += " You are now asked a few questions before the grammar test."

            const = {"participant_id": pid, "random": float(seed),
                     "attcheck1": att1, "attcheck2": att2}

            # Pre-test self-assessments
            for col, q, lo, hi in PRE_ASSESS:
                prompt += f" Question: {q} You answer [HUMAN_RESPONSE]"
                v = agent(prompt, [str(i) for i in range(lo, hi + 1)])
                prompt += f"{v}[/HUMAN_RESPONSE]."
                const[col] = float(v)

            # 20 multiple-choice items
            for trial, qid in enumerate(QIDS):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                info = EXP0_BANK[qid]
                stem = info["stem"].replace('["', " (underlined: ").replace('"]', ")")
                prompt += " Next question. " + stem + " Options:"
                order = _shuffle(seed, len(info["choices"]))
                prompt += " " + " ".join(
                    f"{LETTERS[order.index(i)]}) {info['choices'][i]}" for i in range(len(info['choices'])))
                prompt += " You press [HUMAN_RESPONSE]"
                letter = agent(prompt, [LETTERS[order.index(i)] for i in range(len(info['choices']))])
                idx = order[LETTERS.index(letter)]
                phrase = info["choices"][idx]
                prompt += f"{letter}[/HUMAN_RESPONSE]."
                rows.append({"participant_id": pid, "trial": trial, "response": phrase,
                             "question": qid, **const})

            prompt += " After the test you answer the same questions about your performance."

            # Post-test self-assessments
            for col, q, lo, hi in POST_ASSESS:
                prompt += f" Question: {q} You answer [HUMAN_RESPONSE]"
                v = agent(prompt, [str(i) for i in range(lo, hi + 1)])
                prompt += f"{v}[/HUMAN_RESPONSE]."
                const[col] = float(v)

            prompt += " You also complete a short demographics questionnaire."
            prompts.append(prompt.strip())

            # Patch rows already emitted with the post-test columns.
            for r in rows:
                if r["participant_id"] == pid:
                    for col, _, _, _ in POST_ASSESS:
                        r[col] = const[col]

        cols = (["participant_id", "trial", "response", "question", "random",
                 "attcheck1", "attcheck2"]
                + [c for c, _, _, _ in PRE_ASSESS] + [c for c, _, _, _ in POST_ASSESS])
        df = pd.DataFrame(rows, columns=cols)
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

    task = GrammarSelfAssessment()
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