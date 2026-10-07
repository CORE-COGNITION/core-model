---
tags:
- paradigm:visual-semantics
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
---
# gnther_2023_vispa

- Paper: https://doi.org/10.1037/rev0000392
- Data source: https://osf.io/qvw9c/
- PDF: https://osf.io/download/ebxyu/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Günther, F., Marelli, M., Tureski, S., & Petilli, M. A. (2023). ViSpa (Vision Spaces): A computer-vision-based representation system for individual images and concept prototypes, with large-scale evaluation. Psychological Review, 130(4), 896-934. https://doi.org/10.1037/rev0000392

## Experiment summary
ViSpa (Vision Spaces) tests whether computer-vision (CNN) representation similarities predict human visual semantics. Five studies: St1 (exp0, N=601) and St2 (exp1, N=518) use best-worst similarity ratings — participants pick the most- and least-similar pair among 4 word-pairs (St1) or image-pairs (St2); St3 (exp2, N=933) uses best-worst typicality ratings of images for a category label (5 options); St4 (exp3) is a visual discrimination task reported as item-level aggregated proportion-correct and mean RT; St5 (exp4, N=769) is an image-priming task (identical/different decision) with per-trial RT and accuracy. Participants were paid adults (largely English speakers) giving per-trial ratings/RT responses. ViSpa and layer-wise CNN similarities are compared via GAMs to human judgments; for the rating tasks, `response` is a JSON `{"best": ..., "worst": ...}` of the selected options.

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Original participant ID from source, remapped to P000..P600 in first-appearance order |
| trial | 0..N within each participant, presentation order from source trial_index |
| response | JSON {"best": chosen most-similar word-pair, "worst": chosen least-similar word-pair} from the 4 options; the participant's best-worst selection |
| rt | Response time in ms |
| option1..option4 | The four word-pair answer options on the trial |
| best | The word-pair the participant selected as most similar |
| worst | The word-pair the participant selected as least similar |
| item_id | Unique ID for the set of 4 options; "check" marks a compliance-control item |
| age | Participant age in years |
| gender | Participant gender, canonical f/m/nb/na/other |
| language | Participant's native language |
| compliant_best | Only on "check" items: 1 if the correct "best" option was chosen, else 0; NA otherwise |
| compliant_worst | Only on "check" items: 1 if the correct "worst" option was chosen, else 0; NA otherwise |
| compliant_best_mean | Participant's mean correct "best" over "check" items |
| compliant_worst_mean | Participant's mean correct "worst" over "check" items |
| compliant | 1 if participant met compliance criteria, else 0 |

### exp1
| column | description |
|--------|-------------|
| participant_id | Original participant ID from source, remapped to P000..P517 in first-appearance order |
| trial | 0..N within each participant, presentation order from source trial_index |
| response | JSON {"best": chosen most-similar image-pair, "worst": chosen least-similar image-pair} from the 4 options |
| rt | Response time in ms |
| pair1..pair4 | The four image-pair answer options on the trial (image filenames joined by " - ") |
| best | The image-pair selected as most similar |
| worst | The image-pair selected as least similar |
| item_id | Unique ID for the set of 4 options; "check" marks a compliance-control item |
| age | Participant age in years |
| gender | Participant gender, canonical f/m/nb/na/other |
| language | Participant's native language |
| compliant_best | Only on "check" items: 1 if the correct "best" option was chosen, else 0; NA otherwise |
| compliant_worst | Only on "check" items: 1 if the correct "worst" option was chosen, else 0; NA otherwise |
| compliant_best_mean | Participant's mean correct "best" over "check" items |
| compliant_worst_mean | Participant's mean correct "worst" over "check" items |
| compliant | 1 if participant met compliance criteria, else 0 |

### exp2
| column | description |
|--------|-------------|
| participant_id | Original participant ID from source, remapped to P000..P932 in first-appearance order |
| trial | 0..N within each participant, presentation order = file row order |
| response | JSON {"worst": chosen least-typical image, "best": chosen most-typical image} from the 5 options |
| rt | Response time in ms |
| word | The category word label of a word-image pair |
| option1..option5 | The five image answer options (percentile-morphed images for the word) |
| best | The image selected as most typical |
| worst | The image selected as least typical |
| item_id | Unique ID for the set; an id starting with "p" marks a compliance-control item |
| age | Participant age in years |
| gender | Participant gender, canonical f/m/nb/na/other |
| language | Participant's native language |
| compliant_best | Only on "check" items: 1 if the correct "best" option was chosen, else 0; NA otherwise |
| compliant_worst | Only on "check" items: 1 if the correct "worst" option was chosen, else 0; NA otherwise |
| compliant_best_mean | Participant's mean correct "best" over "check" items |
| compliant_worst_mean | Participant's mean correct "worst" over "check" items |
| compliant | 1 if participant met compliance criteria, else 0 |

### exp3
| column | description |
|--------|-------------|
| participant_id | Single aggregate row set P000: source shipped only item-level (averaged over participants) data, no per-participant IDs |
| trial | 0..N across all item rows |
| response | Percent correct for the item (proportion 0..1, averaged over participants); the only per-item outcome recorded |
| rt | Mean response time in ms, averaged over participants (correct trials only) |
| logRT | log(rt) |
| pair | Image-pair identifier (Image1___Image2, sorted) |
| Image1 | First image in the pair |
| Image2 | Second image in the pair |
| stimulus | The target image shown on the trial (file path) |
| cbow | Language-based (word2vec cbow) similarity of the pair's word labels |
| Value | Human visual-similarity rating of the image pair |
| IMG_Simil_L0..L8, IMG_Simil_HOG | CNN image-based (IMG) similarities per VGG layer / HOG |
| PRO_Simil_L0..L8, PRO_Simil_HOG | CNN prototype-based (PRO) similarities per VGG layer / HOG |

### exp4
| column | description |
|--------|-------------|
| participant_id | Original randomly-generated subject ID from source (e.g. study3_priming_103624), remapped to P000..P768 |
| trial | 0..N within each participant, presentation order = file row order |
| response | Correctness of the identical/different decision: 1 correct, 0 incorrect (raw key-press not recorded in source) |
| rt | Response time in ms |
| stimulus | Target image (file path), identical to img2 when not scrambled |
| img1 | First (prime) image on the trial |
| img2 | Second (target) image on the trial |
| phase | experiment = normal image pair; filler = trials with a scrambled target |
| cbow | Language-based (word2vec cbow) similarity of the pair's word labels (NA on filler trials) |
| Value | Human visual-similarity rating of the image pair (NA on filler trials) |
| age | Participant age in years |
| gender | Participant gender, canonical f/m/nb/na/other |

Study 4 (exp3) is an exception: the source provides only item-level data (proportion correct and mean RT averaged over participants), so exp3 carries a single pseudo-participant (P000) with one row per item rather than per-participant trials. Studies 1-3 and 5 are genuine per-participant trial-level data. `expN` maps to the paper's "Study N": exp0=St1, exp1=St2, exp2=St3, exp3=St4, exp4=St5. Compliance-control ("check") items are retained and tagged via the `compliant*` columns, which are NA on non-check trials.

## Text-format conversion

Transcribed `exp0` (Study 1: best-worst visual-similarity ratings of word pairs) — the stimulus is already text, so participants judging which of four word pairs' referents look most/least visually similar would behave the same reading the transcription. `exp1` (image-pair similarity on photographs), `exp2` (typicality of specific photographs), `exp3`/`exp4` (image-based discrimination and priming RT tasks with only correctness recorded) are not textifiable: the photographic content participants actually judge/see is not expressible in words, and the RT/correctness responses carry no independent choice to transcribe.

Sample transcript (Study 1, participant P001; the first response is fully determined by the instructions alone):

```
This is a study titled 'Which object pair looks the most and least similar?' You judge visual similarity, not category or meaning associations. For example, between the pairs [bottle - pyramid, dog - wolf, lamp - soldier, car - street], dog - wolf looks the most similar and car - street looks the least similar, even though car and street often occur together.
On every trial four word pairs are shown, each naming two everyday objects. Report, in one of these two orders depending on what you judge, the pair whose objects look the most similar and the pair whose objects look the least similar. You state a pair by typing it exactly as shown, e.g. 'dog - wolf'. Give TWO tokens per trial: first your MOST-similar pair, then your LEAST-similar pair. A pair may be chosen for only one of the two positions on a trial.
Options: camp - hound, hedge - clipper, motorcycle - kiss, beach - shore. Most similar: [HUMAN_RESPONSE]beach - shore[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

All five studies were considered. Study 1 was built as `experiments/exp0/`; its headless
`?mode=simulate` round trip passed (CSV columns, dtypes, and counts match `exp0.csv` exactly:
55 rows, `trial` 0-54, the five `check1..check5` catch rows present, compliance means and
`compliant` filled; no outbound data requests; no page/console errors). Studies 2-5
(`exp1`-`exp4`) were skipped: they are image-based (photograph similarity, image typicality,
a discrimination task, and an image-priming task) whose photographic stimuli are not present
in the dataset (only filenames) and cannot be bundled into a single static artifact, so they
could not be built faithfully. This run is therefore `js-experiment:needs-review`. Assumption
worth surfacing: `exp0` embeds a representative 600-item subset of the paper's 24,000
word-pair sets (the full pool is too large for a static artifact), and the catch-item
pre-determined answers for `check1`-`check3` are the modal participant answers in `exp0.csv`
(the paper gives two worked examples). See `experiments/README.md`.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`exp0` (Study 1, best-worst visual-similarity ratings of word pairs) got `simulate0.py`: it generates 55-trial participants (50 individualized word-pair sets drawn from the shipped `exp0.csv` item pool plus the five fixed `check1..check5` catch trials at random positions) and passed the `build_jsonl.py` round trip byte-identically. `exp1`-`exp4` have no transcripts (image-based studies, not textifiable per the Text-format conversion note) and were not simulated. Assumptions: the 24,000 word-pair option sets are recovered verbatim from `exp0.csv` (the paper does not itemize them); the five catch trials emit the pre-determined correct best/worst answers (the modal answers in `exp0.csv`).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
