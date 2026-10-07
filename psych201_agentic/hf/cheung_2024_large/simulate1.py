# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 (Study 2) of ``Hugging-Brain/cheung_2024_large``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

INSTR = 'In this study, you will be shown a moral scenario and you must make a decision about what to do. Read the scenario carefully and choose what you would do. There is no objectively right or wrong answer; you may choose whichever option you think is best. You answer by pressing Y for yes or N for no.'
FRAMED = {'Suicide': {'omission': {'action': 'rule', 'desc': 'You are a member of the parliament in Switzerland and have to vote on a new law. Switzerland’s healthcare expenses are increasing steadily, mainly because the proportion of old people is increasing. In Switzerland, medically assisted suicide has been legal since the 1980s. Recent studies indicate that the delegalization of medically assisted suicide would strongly increase medical expenses. The state considers delegalizing medically assisted suicide for the patients who are terminally ill and whose life expectancy is 6 months or less. If they wish, these patients can currently choose to be killed by a doctor with an overdose of tranquillizers. Experts estimate delegalizing the current law would cost 139 million dollars. This money is currently used for other medical treatments. If you delegalize medically assisted suicide, the healthcare system will have to save money in every possible way. If you allow medically assisted suicide to remain legal, many more people will get better medical treatment improving their quality of life and life expectancy. However, this would continue to allow a form of killing. Do you change the law and make medically assisted suicide illegal? Please answer only with yes or no.'}, 'original': {'action': 'cbr', 'desc': 'You are a member of the Canadian Senate and have to vote on a new law. Canada’s healthcare expenses are increasing steadily, mainly because the proportion of old people is increasing. Recent studies indicate that the legalization of medically assisted suicide would strongly decrease medical expenses. The state considers legalizing medically assisted suicide for the patients who are terminally ill and whose life expectancy is 6 months or less. If they wish, these patients could then choose to be killed by a doctor with an overdose of tranquillizers. Experts estimate that the new law would save 139 million dollars. This money could be used for other medical treatments. If you allow medically assisted suicide, many more people will get better medical treatment improving their quality of life and life expectancy. However, you would legalize a form of killing. If you do not allow medically assisted suicide, the healthcare system will have to keep on saving money in every possible way. Do you change the law and make medically assisted suicide legal? Please answer only with yes or no.'}, 'yesno': {'action': 'rule', 'desc': 'You are a member of the Canadian Senate and have to vote on a new law. Canada’s healthcare expenses are increasing steadily, mainly because the proportion of old people is increasing. Recent studies indicate that the legalization of medically assisted suicide would strongly decrease medical expenses. The state considers legalizing medically assisted suicide for the patients who are terminally ill and whose life expectancy is 6 months or less. If they wish, these patients could then choose to be killed by a doctor with an overdose of tranquillizers. Experts estimate that the new law would save 139 million dollars. This money could be used for other medical treatments. If you allow medically assisted suicide, many more people will get better medical treatment improving their quality of life and life expectancy. However, you would legalize a form of killing. If you do not allow medically assisted suicide, the healthcare system will have to keep on saving money in every possible way. Do you keep the existing law where medically assisted suicide remains illegal? Please answer only with yes or no.'}}, 'Medicine': {'original': {'action': 'rule', 'desc': 'You are the Belgian minister of health. A 7-year-old boy who suffers from a very rare immunological disease asks you for a refund for his medicine. Without taking this medicine regularly, the boy will die. Currently, the medicine is not covered by the health care system, and it is so expensive that the family, who has been buying the medicine for years, will not be able to raise enough money for much longer (approximately 200,000 euros per year). Thus, the boy will die if you refuse the refund. If you refuse to pay for the medicine, the boy will probably die within the next few years. However, if you pay, this money will have to be saved elsewhere; thus, the quality of care for other patients would be reduced, increasing the risk that their treatments will be less effective. An independent agency estimated that funding the boy will therefore likely lead to the death of more people. Do you refund the boy’s medicine? Please answer only with yes or no.'}, 'omission': {'action': 'cbr', 'desc': 'You are the Belgian minister of health. A 7-year-old boy who suffers from a very rare immunological disease asks you for a refund for his medicine. Without taking this medicine regularly, the boy will die. Currently, the medicine is not covered by the health care system, and it is so expensive that the family, who has been buying the medicine for years, will not be able to raise enough money for much longer (approximately 200,000 euros per year). Thus, the boy will die if you refuse the refund. If you refund the boy from the healthcare budget, this money will have to be saved elsewhere; thus, the quality of care for other patients would be reduced, increasing the risk that their treatments will be less effective. An independent agency estimated that funding the boy will therefore likely lead to the death of more people. The next morning, the administrative team sends you a formal request for the money to refund the boy’s medicine. This request will automatically go forward if you do not reject it within the next 24 hours. If you reject the request, the refund will not be processed and the boy will probably die within the next few years. If you do nothing, the request will be processed and the money given to the boy, at the cost of the quality of care for other patients. Do you reject the request? Please answer only with yes or no.'}, 'yesno': {'action': 'cbr', 'desc': 'You are the Belgian minister of health. A 7-year-old boy who suffers from a very rare immunological disease asks you for a refund for his medicine. Without taking this medicine regularly, the boy will die. Currently, the medicine is not covered by the health care system, and it is so expensive that the family, who has been buying the medicine for years, will not be able to raise enough money for much longer (approximately 200,000 euros per year). Thus, the boy will die if you refuse the refund. If you refuse to pay for the medicine, the boy will probably die within the next few years. However, if you pay, this money will have to be saved elsewhere; thus, the quality of care for other patients would be reduced, increasing the risk that their treatments will be less effective. An independent agency estimated that funding the boy will therefore likely lead to the death of more people. Do you keep the money in the budget instead of refunding the boy? Please answer only with yes or no.'}}, 'RAF': {'original': {'action': 'rule', 'desc': 'You are the German head of state in 1977 and a far-left terrorist group kidnapped the President of the Federation of the German Employers’ Association. In exchange for his life, the terrorist group demands the release of 11 imprisoned members. A few years ago, the terrorist group had successfully obtained the release of 5 members by another kidnapping. 4 of the released members have since then committed further terrorist attacks that killed several innocent people. If you consent to the terrorist group’s demands, 11 former terrorists will be released and will likely commit further terrorist attacks killing several people. If you refuse, the hostage will be killed. Do you release the former terrorists? Please answer only with yes or no.'}, 'omission': {'action': 'cbr', 'desc': 'You are the German head of state in 1977 and a far-left terrorist group kidnapped the President of the Federation of the German Employers’ Association. In exchange for his life, the terrorist group demands the release of 11 imprisoned members. A few years ago, the terrorist group had successfully obtained the release of 5 members by another kidnapping. 4 of the released members have since then committed further terrorist attacks that killed several innocent people. If you consent to the terrorist group’s demands, 11 former terrorists will be released and will likely commit further terrorist attacks killing several people. If you refuse, the hostage will be killed. The state minister responsible for this situation tells you that he has already prepared for the former terrorists’ release from prison. However, as a head of state, you have the opportunity to intervene and prevent the release. If you do so, he will not proceed with the release. Do you stop the release of the former terrorists? Please answer only with yes or no.'}, 'yesno': {'action': 'cbr', 'desc': 'You are the German head of state in 1977 and a far-left terrorist group kidnapped the President of the Federation of the German Employers’ Association. In exchange for his life, the terrorist group demands the release of 11 imprisoned members. A few years ago, the terrorist group had successfully obtained the release of 5 members by another kidnapping. 4 of the released members have since then committed further terrorist attacks that killed several innocent people. If you consent to the terrorist group’s demands, 11 former terrorists will be released and will likely commit further terrorist attacks killing several people. If you refuse, the hostage will be killed. Do you keep the former terrorists in prison? Please answer only with yes or no.'}}, 'Vet': {'original': {'action': 'rule', 'desc': 'You are a European veterinarian conducting animal experiments on highly contagious germs. On a daily basis, you cause suffering to animals by infecting them with deadly diseases. You are aware that this work provides important insights that, in the long run, can save many other animals. Furthermore, you are a specialist and because of your expertise you can achieve more than other veterinarians. However, you have become a vet in order to heal animals and you are considering quitting your job. If you quit your job, fewer animals will die in the lab, but there will also be fewer findings about animal diseases. As a result, the development of medicines for healing sick animals will be delayed, leading to many preventable deaths. If you continue your job of infecting animals with diseases for medical research, you will keep causing animal suffering, but your research will probably save the lives of even more animals in the future. Do you quit your job? Please answer only with yes or no.'}, 'omission': {'action': 'cbr', 'desc': 'You are a European veterinarian who is looking for a new job. One day, you receive an email from a medical research institute who offers you a job based on their knowledge of your previous work and expertise. This job involves conducting animal experiments on highly contagious germs. On a daily basis, you would be causing suffering to animals by infecting them with deadly diseases. You are aware that this work provides important insights that, in the long run, can save many other animals. Furthermore, you are a specialist and because of your expertise you can achieve more than other veterinarians. However, you have become a vet in order to heal animals and you are not sure whether you should take up this job. If you do not accept this job, fewer animals will die in the lab, but there will also be fewer findings about animal diseases. As a result, the development of medicines for healing sick animals will be delayed, leading to many preventable deaths. If you accept this job and infect animals with diseases for medical research, you will keep causing animal suffering, but your research will probably save the lives of even more animals in the future. Do you accept this job? Please answer only with yes or no.'}, 'yesno': {'action': 'cbr', 'desc': 'You are a European veterinarian conducting animal experiments on highly contagious germs. On a daily basis, you cause suffering to animals by infecting them with deadly diseases. You are aware that this work provides important insights that, in the long run, can save many other animals. Furthermore, you are a specialist and because of your expertise you can achieve more than other veterinarians. However, you have become a vet in order to heal animals and you are considering quitting your job. If you quit your job, fewer animals will die in the lab, but there will also be fewer findings about animal diseases. As a result, the development of medicines for healing sick animals will be delayed, leading to many preventable deaths. If you continue your job of infecting animals with diseases for medical research, you will keep causing animal suffering, but your research will probably save the lives of even more animals in the future. Do you continue working at your job? Please answer only with yes or no.'}}, 'Endow': {'original': {'action': 'cbr', 'desc': 'After a long-term imprisonment, a convicted child kidnapper and murderer wants to organise a foundation for young victims of crime. You are the president of the agency who decides about the foundation. The founder would donate 25,000 euros to the foundation. However, the foundation would be named after the offender, and it is unclear whether he is acting out of remorse or simply to clear his name. The family of his victim opposes such a foundation and considers it immoral, derogatory, and an exploitation of the victim. If you approve and accept the money for the foundation, crime victims will benefit from the 25,000 euros and additional fund raising. If you oppose the foundation, the money will be lost. Do you approve the foundation? Please answer only with yes or no.'}, 'omission': {'action': 'rule', 'desc': 'You are the president of an agency that oversees a foundation for young victims of crime. This foundation was established because of an anonymous donation of 25,000 euros, with the only requirement being that it is named after a certain man’s name. This male name is quite common and the previous president who established the foundation did not see a problem with it. However, recently, it has come out that the man whom the foundation is named after is actually a convicted child kidnapper and murderer. It appears that he was the one who had donated the money, and it is unclear whether he is acting out of remorse or simply to clear his name. The family of his victim is outraged by this information and considers it immoral, derogatory, and an exploitation of the victim that the foundation is named after him. For legal reasons, you cannot change the name of the foundation, but you can consider whether to close it down. If you close down the foundation, the money will be lost and you cannot help crime victims. If you do nothing, crime victims will benefit from the 25,000 euros and additional fundraising. Do you close down the foundation? Please answer only with yes or no.'}, 'yesno': {'action': 'rule', 'desc': 'After a long-term imprisonment, a convicted child kidnapper and murderer wants to organise a foundation for young victims of crime. You are the president of the agency who decides about the foundation. The founder would donate 25,000 euros to the foundation. However, the foundation would be named after the offender, and it is unclear whether he is acting out of remorse or simply to clear his name. The family of his victim opposes such a foundation and considers it immoral, derogatory, and an exploitation of the victim. If you approve and accept the money for the foundation, crime victims will benefit from the 25,000 euros and additional fund raising. If you oppose the foundation, the money will be lost. Do you oppose the foundation? Please answer only with yes or no.'}}, 'Ransom': {'original': {'action': 'rule', 'desc': 'You are the German head of state and 10 of your citizens are taken hostage in the Sahara Desert by a group of terrorists. You have to decide whether to pay a ransom of several million euros. Other measures to free the hostages have been tried but did not succeed; by now, it has been going on for half a year and one woman has died. Similar situations in the past have shown that terrorists use the money to buy weapons and kill even more people. Furthermore, future tourists will more likely be kidnapped if you pay. If you pay the ransom, you can save the hostages. If you do not pay, the 10 hostages will be killed, but you will prevent future terrorism being financed, which will probably save more than 10 lives. Do you pay the ransom? Please answer only with yes or no.'}, 'yesno': {'action': 'cbr', 'desc': 'You are the German head of state and 10 of your citizens are taken hostage in the Sahara Desert by a group of terrorists. You have to decide whether to pay a ransom of several million euros. Other measures to free the hostages have been tried but did not succeed; by now, it has been going on for half a year and one woman has died. Similar situations in the past have shown that terrorists use the money to buy weapons and kill even more people. Furthermore, future tourists will more likely be kidnapped if you pay. If you pay the ransom, you can save the hostages. If you do not pay, the 10 hostages will be killed, but you will prevent future terrorism being financed, which will probably save more than 10 lives. Do you leave the hostages to their fate? Please answer only with yes or no.'}, 'omission': {'action': 'cbr', 'desc': 'You are the German head of state and 10 of your citizens are taken hostage in the Sahara Desert by a group of terrorists. You have to decide whether to pay a ransom of several million euros. Other measures to free the hostages have been tried but did not succeed; by now, it has been going on for half a year and one woman has died. Similar situations in the past have shown that terrorists use the money to buy weapons and kill even more people. Furthermore, future tourists will more likely be kidnapped if you pay. If you pay the ransom, you can save the hostages. If you do not pay, the 10 hostages will be killed, but you will prevent future terrorism being financed, which will probably save more than 10 lives. The state minister responsible for this situation tells you that he has already prepared the money to give to the terrorists, and he can arrange for it to be delivered safely in exchange for the hostages. He asks if you object to this decision. If you object, he will not proceed with the payment. Do you object to paying the ransom? Please answer only with yes or no.'}}}
FRAMING_KEY = {'base': 'original', 'yesno': 'yesno', 'omission': 'omission'}
DILEMMAS = ['Suicide', 'Medicine', 'RAF', 'Vet', 'Endow', 'Ransom']
FRAMINGS = ['base', 'yesno', 'omission']
CHOICES = ['Y', 'N']



class Study2Survey:
    """Study 2 (Cheung, Maier & Lieder 2024): one framed sacrificial dilemma
    per participant (between-subjects), answered yes (Y) or no (N).

    Design (Materials and Methods, Study 2, p. 21): participants were randomly
    assigned to one of 18 vignettes (6 dilemmas x 3 framings) and answered
    yes or no.

    ASSUMPTION: the (dilemma, framing) pair per simulated participant is drawn
    uniformly over the 18 possibilities.

    ASSUMPTION: the yes/no token is fixed Y/N; response 1 (yes) -> Y,
    response 0 (no) -> N, as in exp1.csv and build_jsonl.py.

    ASSUMPTION: the trailing " Please answer only with yes or no." is stripped
    from the vignette before the response, exactly as in build_jsonl.py.

    The DataFrame matches exp1.csv minus the Qualtrics metadata columns.
    """

    def __init__(self):
        self.name = "cheung_2024_large_exp1"
        self.dilemmas = list(DILEMMAS)
        self.framings = list(FRAMINGS)
        self.choices = list(CHOICES)

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for sim in tqdm(range(num_simulations)):
            dit = str(np.random.choice(self.dilemmas))
            fram = str(np.random.choice(self.framings))
            vig = FRAMED[dit][FRAMING_KEY[fram]]["desc"]
            vig = vig.replace(" Please answer only with yes or no.", "").strip()
            prompt = INSTR + "\n"
            prompt += f"\nDilemma ({dit}, {fram} framing): {vig}\n"
            prompt += "You press [HUMAN_RESPONSE]"
            token = str(agent(prompt, choice_options=self.choices))
            prompt += token + "[/HUMAN_RESPONSE].\n"
            rows.append(
                {"participant_id": f"P{sim:03d}", "trial": 0,
                 "response": 1.0 if token == "Y" else 0.0, "dilemma": dit, "framing": fram,
                 "phase": "test", "valid": 1})
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "dilemma", "framing",
            "phase", "valid",
        ])
        df["response"] = df["response"].astype("float64")
        return df, prompts



def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3,
                        help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None,
                        help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None,
                        help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = Study2Survey()
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
