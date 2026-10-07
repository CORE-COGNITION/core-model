# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/jansen_2021_rational`` (Logical
Reasoning / LSAT study, Study 2 of Jansen, Rafferty & Griffiths, 2021),
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
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
EXP1_ATT1 = ["Grammar", "Logical reasoning", "Creative writing"]
EXP1_ATT2 = ["The best choice", "The longest choice", "All of the choices that are correct"]

LETTERS = "ABCDE"

EXP1_BANK = {
    'Q1': {"stem": 'Life imitates art. Which of the following, if true, most strongly supports the previous statement?', "choices": ['When Warren Beatty filmed Reds, he tried to suggest not only the chaos of the Russian Revolution but also its relationship to the present.', 'The number of professional ballet companies has increased over the last five years, but the number of dance majors has decreased.', 'On Tuesday, the business section of the newspaper had predicted the drop in interest rates that occurred on Friday.', 'Truman Capote wrote In Cold Blood as a result of a series of brutal slayings by two crazed killers.', 'Soon after the advent of color television, white shirts became less popular as dressy attire for men, and pastel-colored shirts began to sell well.']},
    'Q2': {"stem": 'On average, federal workers receive salaries 35.5 percent higher than private-sector salaries. For instance, federal workers in California average $19,206 a year, 25 percent higher than the average pay in the private sector, which is $15,365. This information would best support which of the following opinions?', "choices": ['Private-sector salaries in California are above average.', 'The private sector is being paid fairly.', 'Federal jobs are more secure than private-sector jobs.', 'Public-sector work is more difficult than private-sector work.', 'Federal pay is out of line.']},
    'Q3': {"stem": 'No high jumper entered the track meet unless he or she was a track club member. No track club member both entered the meet and was a high jumper. Which of the following conclusions can be correctly drawn from the two previous sentences?', "choices": ['No one but high jumpers entered the meet.', 'Only track club members entered the meet.', 'No track club members entered the meet.', 'No high jumper entered the meet.', 'Some track club members entered the meet.']},
    'Q4': {"stem": 'About 33% of American men between 25 and 50 are overweight. Research has shown that in most cases men between 25 and 50 who are overweight are more subject to heart disease than men who are not overweight. Which of the following is the most logical conclusion to this argument?', "choices": ['Therefore, 33% of the American men between 25 and 50 should lose weight.', 'Therefore, if 33% of the American men between 25 and 50 were to lose weight, they would reduce their risk of heart disease.', 'Therefore, if the men between 25 and 50 who are overweight were to lose weight, they would reduce their risk of heart disease by 33%.', 'Therefore, if 33% of American men were to lose weight, they would reduce their risk of heart disease.', 'Therefore, if the overweight men between 25 and 50 were to lose weight, their risk of heart disease would be reduced.']},
    'Q5': {"stem": 'All computer geniuses are also brilliant mathematicians. Therefore, some computer geniuses don’t require calculators for simple multiplication facts. Which of the following is the least necessary assumption for the previous conclusion to be logically correct?', "choices": ['Some brilliant mathematicians don’t require calculators for simple multiplication facts.', 'All brilliant mathematicians don’t require calculators for simple multiplication facts.', 'Some brilliant mathematicians require calculators for simple multiplication facts.', 'All computer geniuses who require calculators for simple multiplication facts are brilliant mathematicians.', 'Only computer geniuses are also brilliant mathematicians.']},
    'Q6': {"stem": 'A researcher has concluded that women are just as capable as men in math but that their skills are not developed because society expects them to develop other and more diverse abilities. Which of the following is a basic assumption of the researcher?', "choices": ['Ability in math is more important than ability in more diverse subjects.', 'Ability in math is less important than ability in more diverse subjects.', 'Women and men should be equally capable in math.', 'Women might be more capable than men in math.', 'Women tend to conform to social expectations.']},
    'Q7': {"stem": 'Jonathan Swift said, “Laws are like cobwebs which may catch small flies but let wasps and hornets break through.” Jonathan Swift would most likely believe that', "choices": ['prosecutors should be tough on criminals', 'pesticides should be used to deter large insects', 'small crimes should not be prosecuted', 'the powerful can often avoid serious criminal sentences', 'laws do not stop people from committing crimes']},
    'Q8': {"stem": 'When Mom cooks, we all eat a delicious dinner. But Mom didn’t cook today, so we won’t be eating a delicious dinner. Which of the following is logically most similar to the previous argument?', "choices": ['When food is cooked, it always burns. But our food isn’t burned, so therefore it wasn’t cooked.', 'When silverware is used at the dining table, we usually have guests. Today we have guests, so we are using the silverware.', 'When the dog has fleas, he always scratches. But the dog doesn’t have fleas, so he won’t be scratching.', 'When a person is fortunate, he or she has great good luck. So a fortunate person will always be lucky.', 'When a university finishes admitting entering students, the freshman class is complete. Since the freshman class is not complete, the university has not finished admitting entering students.']},
    'Q9': {"stem": 'Without sign ordinances, everyone with the price of a can of spray paint can suddenly decide to publicly create their own personal Picassos, and soon the entire town would start to look like something out of Alice in Wonderland. Therefore we need sign ordinances. All of the following are assumptions underlying the previous argument EXCEPT', "choices": ['spray paint can be used to create graffiti', 'the town looking like Alice in Wonderland is undesirable', 'sign ordinances are effective', 'no other effective means of deterring graffiti presently exist', 'sign ordinances are rarely, if ever effective']},
    'Q10': {"stem": 'When Louis Pasteur said, “Chance favors the prepared mind,” the famous French scientist most nearly meant', "choices": ['take a chance only if you’re prepared', 'pasteurization was a chance that Pasteur prepared for', 'being prepared will be favorable to those who take chances', 'happenstance will be more beneficial to those who are prepared', 'we all have a chance to be prepared']},
    'Q11': {"stem": 'All acts have consequences. Given this fact, we may wish to play it safe by never doing anything. The speaker implies that', "choices": ['we may prefer to live safely', 'all acts have consequences', 'consequentiality is not safe', 'doing nothing has lesser consequences', 'not doing anything is not an act']},
    'Q12': {"stem": 'Voltaire once said, “Common sense is not so common.” Which of the following most nearly parallels Voltaire’s statement?', "choices": ['God must have loved the common man; he certainly made enough of them.', 'The common good is not necessarily best for everyone.', 'Jumbo shrimp may not actually be very big.', 'Good people may not necessarily have good sense.', 'Truth serum cannot contain the truth.']},
    'Q13': {"stem": 'It has been proven that the “lie detector” can be fooled. If one is truly aware that one is lying, when in fact one is, then the “lie detector” is worthless. The author of this argument implies that', "choices": ['the lie detector is a useless device', 'a good liar can fool the device', 'a lie detector is often inaccurate', 'the lie detector is sometimes worthless', 'no one can fool the lie detector all of the time']},
    'Q14': {"stem": 'It has been proven that the “lie detector” can be fooled. If one is truly aware that one is lying, when in fact one is, then the “lie detector” is worthless. This argument would be strengthened most by', "choices": ['demonstrating that one’s awareness of truth or falsity is always undetectable', 'citing evidence that there are other means of measuring truth which are consistently less reliable than the lie detector', 'citing the number of cases in which the lie detector mistook falsehood for truth', 'claiming that ordinary, unbiased people are the best “lie detectors”', 'showing that the “truth” of any statement always relies on a subjective assessment']},
    'Q15': {"stem": 'It has been proven that the “lie detector” can be fooled. If one is truly aware that one is lying, when in fact one is, then the “lie detector” is worthless. Without contradicting his or her own statements, the author of the above statement might present which of the following arguments as a strong point in favor of the lie detector?', "choices": ['The methodology used by investigative critics of the lie detector is itself highly flawed.', 'Circumstantial evidence might be more useful in a criminal case than is personal testimony.', 'The very threat of a lie-detector test has led to a significant number of criminals to confess.', 'People are never “truly unaware” that they are lying.', 'Law-enforcement agencies have purchased too many detectors to abandon them now.']},
    'Q16': {"stem": 'English automobiles leak oil. All sportscars need some repair every month. Since the vehicle I recently purchased leaks oil and needs repair every month, I must have purchased an English sportscar. Which of the following, if true, would logically weaken the previous conclusion?', "choices": ['Only English sportscars need repair every month.', 'Not all English sedans leak oil.', 'Some sportscars need repair every two weeks.', 'Danish automobiles also leak oil.', 'American sportscars never need repair.']},
    'Q17': {"stem": 'By appropriating bailout money for the depressed housing industry, Congress is opening the door to a flood of special relief programs for other recession-affected businesses. The author’s attitude toward the Congress’ action is probably', "choices": ['neutral', 'disapproving', 'confused', 'happy', 'irate']},
    'Q18': {"stem": 'We have been warned that if we stop watering our lawn, then not only will our grass die and our trees turn brown, but also the gophers will find the dry, hard soil a stimulus for ravaging whatever vegetation happens to survive. Therefore, we have decided to continue to water our lawn. All of the following can be reasonably inferred as goals of the author except', "choices": ['the grass is not dying', 'the trees not turning brown', 'the gophers not ravaging remaining vegetation', 'the soil not becoming dry and hard', 'water conservation']},
    'Q19': {"stem": 'According to a recent study by the National Academy of Public Administration, postal patrons are regularly affronted by out-of-order stamp vending machines, branch post office lobbies locked at night, and twenty-nine cent letters that take as long to get there as thirteen-cent letters did a decade ago. Which of the following, if true, would weaken the implication of one of the author’s observations?', "choices": ['Most out-of-order vending machines are located in run-down neighborhoods.', 'Late-night vandalism has plagued post offices nationwide.', 'Postage rates rose over a hundred percent from 1983 to 1993, but the cost of first class mail is still cheaper in the US than anywhere else.', 'As a public corporation, the Postal Service has increased its capital assets by $3 billion.', 'Ten years ago, most letters reached their destination within twenty-four hours.']},
    'Q20': {"stem": 'If I do not get at least a B on the final exam, I will definitely fail my geology course. From the previous statement, it most logically follows that if I do get a B on the final exam in geology, I then', "choices": ['may or may not pass the course', 'will definitely pass the course', 'will probably not pass the course', 'will probably pass the course', 'will definitely not pass the course']},
}

QIDS = [f"Q{i}" for i in range(1, 21)]

# Pre-test self-assessment specs: (column, narration question, min value, max value).
PRE_ASSESS = [
    ("logicAssess0_1",
     "Compared to other participants in this study, how would you rate  your general logical "
     "reasoning ability? (a number from 0 to 100)", 0, 100),
    ("absAssess0", "How many of the 20 logical reasoning problems do you think you will solve correctly? (a number from 0 to 20)", 0, 20),
    ("relAssess0_1", "Compared to other participants in this study, how well do you think you will do? (a number from 0 to 100)", 0, 100),
    ("diffSelf0_1", "How difficult is solving logical reasoning problems for you? (1 = very easy, 10 = very difficult)", 1, 10),
    ("diffOther0_1", "How difficult is solving logical reasoning problems for the average participant? (1 = very easy, 10 = very difficult)", 1, 10),
]

POST_ASSESS = [
    ("logicAssess1_1",
     "Compared to other participants in this study, how would you rate  your general logical "
     "reasoning ability? (a number from 0 to 100)", 0, 100),
    ("absAssess1", "How many of the 20 logical reasoning problems you just completed do you think you answered correctly? (a number from 0 to 20)", 0, 20),
    ("relAssess1_1", "Compared to other participants in this study, how well do you think you performed? (a number from 0 to 100)", 0, 100),
    ("diffSelf1_1", "How difficult was solving these logical reasoning problems for you? (1 = very easy, 10 = very difficult)", 1, 10),
    ("diffOther1_1", "How difficult was solving these logical reasoning problems for the average participant? (1 = very easy, 10 = very difficult)", 1, 10),
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


class LogicalReasoningSelfAssessment:
    """Logical-reasoning / LSAT study (Study 2) of Jansen, Rafferty & Griffiths
    (2021), "A rational model of the Dunning-Kruger effect supports insensitivity
    to evidence in low performers", Nature Human Behaviour 5, 756-763.

    Session structure (Study 2, Methods/Procedure; recovered from the shipped
    transcripts and build_jsonl.py because the article body is paywalled at
    nature.com): consent + instructions; two fixed-order comprehension checks
    (subject, best choice); five pre-test self-assessments (0-100 relative
    ability, 0-20 absolute count, 0-100 relative performance, two 1-10
    difficulty scales); 20 multiple-choice LSAT logical-reasoning items each
    with 5 choices; five post-test self-assessments; demographics note.

    The participant's 20 answers are chosen freely by the agent among the 5
    shuffled options; the five self-assessment values are drawn by the agent
    uniformly over each item's integer scale. Option lettering for the 20 items
    is shuffled per participant from the stored ``random`` seed exactly as
    build_jsonl.py does, so the round trip is byte-identical.

    The DataFrame matches exp1.csv minus demographic/timing columns (age,
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
        self.name = "jansen_2021_rational_exp1"
        self.num_questions = 20

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = f"SIM{participant:05d}"
            seed = int(np.random.randint(100000, 999999))

            prompt = ("You are taking part in a study on how people perceive their own abilities. "
                      "You first read an informed-consent statement and then decide to continue. "
                      "The task instructions say: 'In this task, you're going to be answering a set of 20 questions "
                      "about logical reasoning. You will be presented with brief passages or statements and will be "
                      "required to evaluate their reasoning or determine what inferences you can logically draw from "
                      "the passage. In each case, select the best answer choice, even though more than one choice may "
                      "present a possible answer.' On every question you press the letter of the option you choose (A, B, C, ...).")

            # Comprehension check 1
            prompt += (" First you must pass a short comprehension test. Question: 'What subject are you going to be "
                       "answering questions about?' Options: ")
            prompt += " ".join(LETTERS[i] + ") " + o for i, o in enumerate(EXP1_ATT1))
            prompt += " You press [HUMAN_RESPONSE]"
            l1 = agent(prompt, ["A", "B", "C"])
            prompt += f"{l1}[/HUMAN_RESPONSE]."
            att1 = EXP1_ATT1["ABC".index(l1)]

            # Comprehension check 2
            prompt += " Question: 'Which answer choice should you select?' Options: "
            prompt += " ".join(LETTERS[i] + ") " + o for i, o in enumerate(EXP1_ATT2))
            prompt += " You press [HUMAN_RESPONSE]"
            l2 = agent(prompt, ["A", "B", "C"])
            prompt += f"{l2}[/HUMAN_RESPONSE]."
            att2 = EXP1_ATT2["ABC".index(l2)]

            prompt += " You are now asked a few questions before the test."

            const = {"participant_id": pid, "random": int(seed),
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
                info = EXP1_BANK[qid]
                prompt += " Next question. " + info["stem"] + " Options:"
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

    task = LogicalReasoningSelfAssessment()
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