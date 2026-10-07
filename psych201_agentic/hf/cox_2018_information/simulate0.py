# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/cox_2018_information``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0).
INTRO = (
    "You are taking part in a memory experiment with five tasks: single-item recognition, "
    "associative recognition, cued recall, free recall, and lexical decision. Each task "
    "(except lexical decision) begins with a study phase in which 20 word pairs are presented "
    "one at a time, each for 2 seconds. Immediately after each pair you rate how associated the "
    "two words are on a scale from 1 to 9, by typing the number. The study phase is followed by "
    "a 45-second math distractor task, and then a memory test. Each of the five tasks is "
    "repeated three times, for 15 study/test blocks in total; the tasks appear in a different "
    "order each time."
)

TASK_NAMES = {0: "Associative recognition", 1: "Cued recall", 2: "Free recall",
              3: "Lexical decision", 4: "Single item recognition"}

CONDITION = {0: "associative_recognition", 1: "cued_recall", 2: "free_recall",
             3: "lexical_decision", 4: "single_recognition"}

TEST_INSTR = {
    0: "Associative recognition test: for each pair, press Y if the pair was studied together "
       "(old) or N if it is a rearranged, new pair.",
    1: "Cued recall test: for each cue word, type the other word from the studied pair. If you "
       "cannot recall it, click DON'T REMEMBER.",
    2: "Free recall test: type as many words from the study list as you can remember.",
    3: "Lexical decision test: for each letter string, press Y if it is a word or N if it is "
       "not a word. Respond as quickly as possible.",
    4: "Single-item recognition test: for each word, press Y if the word was on the list you "
       "just studied (old) or N if it was not (new).",
}

COLS = ["participant_id", "trial", "task_id", "block", "phase", "condition",
        "trial_in_block", "block_source", "stim.string.left", "stim.string.right",
        "stim.distractor", "studied", "distractor.resp", "response", "resp.string",
        "resp.type"]


WORDS = ['ABILITY', 'ABOUT', 'ACCIDENT', 'ACCOANED', 'ACCOUNT', 'ACCOUNTS', 'ACCURATE', 'ACHEIVE', 'ACHIEVE', 'ACID', 'ACLEAVE', 'ACTED', 'ADANPY', 'ADDING', 'ADDRESS', 'ADEGRENT', 'ADEQUATE', 'ADHACE', 'ADHALLS', 'ADMINISTRATION', 'ADOPTED', 'ADOW', 'ADSTE', 'ADULTS', 'ADVANCE', 'ADVANCED', 'ADVANTAGES', 'ADVICE', 'ADVIGENT', 'AFFAIRS', 'AFFALLS', 'AFFECK', 'AFFECTS', 'AFFFECT', 'AFFICAN', 'AFFOIDS', 'AFFORD', 'AFRICA', 'AFRICAN', 'AFTUL', 'AFUKE', 'AGENCY', 'AGES', 'AGOLTS', 'AGREEMENT', 'AGRICULTURE', 'AGRIECANT', 'AHRIESTS', 'AINT', 'ALCUAT', 'ALDECTS', 'ALLACE', 'ALLOWS', 'ALLWOED', 'ALRYMENT', 'AMBINTADES', 'AMBUME', 'AMILYFOS', 'AMMORCHED', 'AMSTACTIZE', 'ANALYSIS', 'AND', 'ANDANGED', 'ANDOUCHED', 'ANGER', 'ANICTMENT', 'ANLIDLE', 'ANNIE', 'ANNOUNCE', 'ANNOUNCED', 'ANNUAL', 'ANSARGEMENT', 'ANSON', 'APARTMENT', 'APPARENTLY', 'APPHESS', 'APPLE', 'APPLICATION', 'APPLY', 'APPOINTED', 'APPOINTMENT', 'APPOMOZISE', 'APPROPRIATE', 'APPROVEMENT', 'APURGED', 'ARBER', 'ARBUPT', 'ARGUED', 'ARGUMENT', 'ARGUMENTS', 'ARMED', 'ARRANGED', 'ARRANGEMENT', 'ARTICLE', 'AS', 'ASKING', 'ASLEEP', 'ASOCIATE', 'ASPECTS', 'ASSAIMED', 'ASSEMBLE', 'ASSEMBLEY', 'ASSEMBLY', 'ASSEMIATE', 'ASSICTRY', 'ASSIGNED', 'ASSOCIATED', 'ASSUME', 'ASTINIDE', 'ASTRY', 'ATOM', 'ATRUMATE', 'ATTACHED', 'ATTALICTRATION', 'ATTEMPTS', 'ATTINGED', 'ATTIPSED', 'ATTITUDE', 'ATTRACTIVE', 'AUDIENCE', 'AUDITULTUDE', 'AUNT', 'AUTHECLIATE', 'AUTHOR', 'AUTHORITY', 'AUTOMOBILE', 'AWAITS', 'AWAKE', 'AWBLOR', 'AWFUL', 'AWNED', 'AWROUP', 'AXIN', 'AYCIRAN', 'BACIN', 'BACKGROUND', 'BACKTHOUSE', 'BACTERIA', 'BADLY', 'BAG', 'BAK', 'BALT', 'BAM', 'BAMPERATEDES', 'BAMS', 'BANCTALL', 'BAND', 'BANES', 'BANKS', 'BANSITORY', 'BARE', 'BARN', 'BASEBALL', 'BAULING', 'BAWS', 'BAY', 'BEACH', 'BEANCIL', 'BEAP', 'BEAT', 'BEATH', 'BEAUTY', 'BEDERATUDE', 'BEDROOM', 'BEENTY', 'BEGING', 'BEING', 'BEINGS', 'BEIRATY', 'BELIEF', 'BELIEFS', 'BELL', 'BELONG', 'BENEFIT', 'BENEFITS', 'BENT', 'BERANG', 'BERE', 'BEROED', 'BEROOF', 'BESS', 'BICCER', 'BIG', 'BIGGER', 'BILLER', 'BILLION', 'BINGENAY', 'BIRTHDAY', 'BITS', 'BITTER', 'BITTING', 'BLACK', 'BLACKS', 'BLASSED', 'BLAYS', 'BLEASED', 'BLECKS', 'BLEW', 'BLIANLY', 'BLIND', 'BLITE', 'BLOCKS', 'BLOW', 'BOANS', 'BOATS', 'BOBBLE', 'BOCUNALLY', 'BODERITION', 'BOMOABLE', 'BONE', 'BONK', 'BOOGTY', 'BOOTS', 'BOTTLE', 'BOULE', 'BOUND', 'BOX', 'BOXES', 'BRACK', 'BRANCH', 'BRANING', 'BRASED', 'BRASING', 'BREAKING', 'BREATHE', 'BRICK', 'BRIDGE', 'BRIEF', 'BRIGHT', 'BRINGING', 'BROAF', 'BROCK', 'BROTHERS', 'BRUDIT', 'BRUNK', 'BRUSH', 'BUD', 'BUGROOM', 'BUIES', 'BUILDING', 'BUNESAT', 'BUR', 'BURBS', 'BURD', 'BURIED', 'BURN', 'BURST', 'BUS', 'BUTS', 'BUYING', 'BYSCE', 'CABIN', 'CACKS', 'CADAGRA', 'CADERS', 'CADY', 'CAFE', 'CALE', 'CALLING', 'CALLS', 'CALM', 'CALOOR', 'CAMBLE', 'CAMP', 'CAMPAIGN', 'CAMPING', 'CAMPOSTE', 'CAND', 'CANG', 'CANNIES', 'CAP', 'CAPABLE', 'CAPACITY', 'CARD', 'CAREER', 'CARRIES', 'CARRY', 'CASH', 'CASLY', 'CAST', 'CATOFY', 'CATRINENT', 'CATTLE', 'CAUSING', 'CAZE', 'CEIGNS', 'CENTERS', 'CHACE', 'CHAIN', 'CHAIR', 'CHALLENGE', 'CHALOW', 'CHARACTERISTIC', 'CHARACTERS', 'CHARED', 'CHARGED', 'CHARNED', 'CHART', 'CHAYS', 'CHECKED', 'CHEET', 'CHEETMENT', 'CHEMICALS', 'CHEXTER', 'CHILD', 'CHILDREN', 'CHINA', 'CHINESE', 'CHITED', 'CHOSE', 'CHRISMAS', 'CHRISTIAN', 'CHRISTMAS', 'CHUSE', 'CICIOES', 'CILLEIN', 'CIRCIRSPENCES', 'CIRCUMSTANCES', 'CIVILIZATION', 'CLAIM', 'CLANTER', 'CLASS', 'CLASSIFIED', 'CLASSROOM', 'CLAUD', 'CLAY', 'CLEALURE', 'CLEATHE', 'CLECOADIZED', 'CLENTINY', 'CLERRIFIED', 'CLIB', 'CLIDGE', 'CLIENT', 'CLIMB', 'CLIRER', 'CLISP', 'CLOAD', 'CLOPE', 'CLOSENESS', 'CLOTH', 'CLOUD', 'CLUB', 'CLUMERY', 'COAK', 'COAT', 'COATLE', 'COCTEE', 'CODDER', 'CODOLESTS', 'COFFEE', 'COLD', 'COLLECT', 'COLLECTION', 'COLLICS', 'COLLON', 'COLONIAL', 'COLONISTS', 'COLONY', 'COLUMN', 'COMBENT', 'COMBERPEAL', 'COMBINATION', 'COMBINE', 'COMBIRE', 'COMBOLLS', 'COMBOUNT', 'COMFORTABLE', 'COMMAND', 'COMMEDS', 'COMMERCIAL', 'COMMESTIA', 'COMMIT', 'COMMITMENT', 'COMMITTEE', 'COMMONLY', 'COMMUNICATE', 'COMMUNIST', 'COMMUNITIES', 'COMPARA', 'COMPARE', 'COMPARILATE', 'COMPATIST', 'COMPETITION', 'COMPISLY', 'COMPLETED', 'COMPLEX', 'COMPLICATED', 'COMPOSED', 'COMPOUND', 'COMPS', 'COMPUTER', 'COMSHONED', 'CONCEPT', 'CONCHRINTION', 'CONCLUCT', 'CONDUCT', 'CONFIDENCE', 'CONFLICT', 'CONGAPT', 'CONGIVER', 'CONGLILS', 'CONNECTED', 'CONNUKE', 'CONSANTED', 'CONSENT', 'CONSHIST', 'CONSIDERABLE', 'CONSTALL', 'CONSTANTLY', 'CONSTRUCTION', 'CONSUMER', 'CONTAINED', 'CONTENT', 'CONTINENT', 'CONTINENTS', 'CONTINUES', 'CONTIQUES', 'CONTITOME', 'CONTRACT', 'CONTRAST', 'CONTROL', 'CONTROLS', 'CONVERSATION', 'CONVIGANCE', 'CONWRESHLY', 'COOK', 'COPPER', 'COPY', 'CORCERRABLE', 'CORRARITIES', 'CORRUNER', 'CORTELL', 'COSSORITION', 'COSTOCTION', 'COSTS', 'COSUAL', 'COTTON', 'COUGHT', 'COUL', 'COUNCE', 'COUNCIL', 'COUNT', 'COUNTY', 'COUPLE', 'COURTS', 'COVERS', 'CRAIN', 'CREAM', 'CREATURE', 'CREDIT', 'CREW', 'CREY', 'CRIDE', 'CRIME', 'CRIP', 'CRITHERS', 'CRITICAL', 'CROHL', 'CROP', 'CROPS', 'CROWD', 'CROWDED', 'CRYING', 'CULTURAL', 'CUP', 'CUPSARAL', 'CURIOUS', 'CUSTAND', 'CUSTOM', 'CUSTOMER', 'CUSTOMS', 'CUTTING', 'CUTTUCER', 'CYCLE', 'DAD', 'DALT', 'DAMAGE', 'DAMAGED', 'DANCE', 'DANGEROUS', 'DAOPLES', 'DAP', 'DARKNESS', 'DARKS', 'DAT', 'DAWN', 'DEBISE', 'DEBLOUS', 'DECASIONS', 'DECIGIAN', 'DECISION', 'DECLARED', 'DED', 'DEEPLY', 'DEFENSE', 'DEFICHABLE', 'DEFINED', 'DEFINITE', 'DEFINITION', 'DEGANED', 'DEGREE', 'DEGREES', 'DEIRS', 'DELINDS', 'DEMANDS', 'DEMILEGING', 'DENEADES', 'DENMAVERY', 'DEPENDENT', 'DEPRESSION', 'DEPRIRED', 'DESAMP', 'DESCRIPTION', 'DESIGN', 'DESIRE', 'DESISTENT', 'DESPLEXTION', 'DESTARSION', 'DESTRAM', 'DESTROY', 'DESTRUCTION', 'DETAIL', 'DETICS', 'DEVELOP', 'DEVELOPING', 'DEVERLOPP', 'DEVICE', 'DEVOLE', 'DEYILOTE', 'DIAPPOINT', 'DICARTED', 'DID', 'DIDRINATION', 'DIFERENT', 'DIFFER', 'DIFFICULT', 'DIFFICULTY', 'DIMBADERABLE', 'DIMENIAL', 'DINMERKATION', 'DIORDER', 'DIOXIDE', 'DIPPICITTY', 'DIRECTED', 'DIRECTIONS', 'DIRT', 'DIRTLY', 'DISAMBEERED', 'DISAPPEARED', 'DISBUTS', 'DISCOVERY', 'DISCUSS', 'DISEASES', 'DISGRICATED', 'DISSING', 'DISTANCE', 'DISTANT', 'DISTINE', 'DIVISION', 'DOCIFIMATION', 'DOCTORS', 'DOLLAR', 'DOMECITY', 'DOMENESS', 'DON', 'DOOR', 'DOORS', 'DOUBLE', 'DOWAGE', 'DOZEN', 'DR', 'DRANTROOM', 'DREALANT', 'DREAM', 'DRIED', 'DRIG', 'DRIGHTENTS', 'DRIM', 'DRINKING', 'DRISMERED', 'DRIVER', 'DROCKS', 'DRUG', 'DRULLING', 'DRUNK', 'DULL', 'DUMS', 'DURRY', 'DURT', 'DUTY', 'EADER', 'EAGER', 'EAR', 'EARD', 'EARLIEST', 'EARN', 'EATEN', 'ECOSTION', 'EDARTOUS', 'EDES', 'EDMANTIVELY', 'EDSHY', 'EDTEND', 'EDUCATION', 'EDUCATION BURST', 'EDUCATIONAL', 'EFFECTIVELY', 'EFFICIENT', 'EGG', 'EIR', 'ELAPSED', 'ELBOSED', 'ELDED', 'ELDING', 'ELECTION', 'ELECTRICAL', 'ELECTRONS', 'ELEMENT', 'ELL', 'EMACTRINS', 'EMAPE', 'EMATUTIDE', 'EMENY', 'EMOTIONAL', 'EMOTIONS', 'EMPIRE', 'EMPLAXIAS', 'EMPLOYEES', 'EMPOTE', 'EMURIALAL', 'ENANGE', 'ENCH', 'ENCOURAGED', 'ENDRYENCED', 'ENEMY', 'ENGATE', 'ENGINE', 'ENGUFIATED', 'ENJOYED', 'ENJUMED', 'ENMERINANT', 'ENORMOUS', 'ENSBYGAY', 'ENSCUMATION', 'ENSEARACED', 'ENSIRATE', 'ENSOCIENTES', 'ENSTAWED', 'ENSURE', 'ENTERPOL', 'ENTINSED', 'ENTRANCE', 'ENTRY', 'EPPICOUNT', 'EQUALLY', 'ERA', 'ERV', 'ESANT', 'ESCAPE', 'ESCHASTE', 'ESECANT', 'ESFULLENT', 'ESINTESTS', 'ESPENNISM', 'ESPIPE', 'ESSLESS', 'ESTABLISH', 'ESTAILERN', 'ESYL', 'ETO', 'ETUNOTIALAL', 'ETVERGAL', 'EUBER', 'EUROPE', 'EUROPEANS', 'EVENT', 'EVERYDAY', 'EVIL', 'EVISPRICAL', 'EWREDLY', 'EXACT', 'EXAMINE', 'EXBRAIRED', 'EXCELLENT', 'EXCERSISE', 'EXCETSION', 'EXCHANGE', 'EXCITED', 'EXCITEMENT', 'EXCITMENT', 'EXCLAIMED', 'EXCLAME', 'EXCLOSE', 'EXECUTIVE', 'EXERCISE', 'EXERDAMS', 'EXEXISM', 'EXIST', 'EXISTENCE', 'EXIT', 'EXPANSION', 'EXPENSIVE', 'EXPERIENCE', 'EXPERIENCES', 'EXPERIMENT', 'EXPIRE', 'EXPLANATION', 'EXPLANIED', 'EXPLORE', 'EXPOSED', 'EXPRESS', 'EXTENT', 'EXTERNAL', 'EXTOILMENT', 'EXTREAME', 'EXTREME', 'FABBOR', 'FACING', 'FACTOR', 'FACTORY', 'FACURES', 'FAILURE', 'FAIR', 'FAIRLY', 'FALATION', 'FALE', 'FALLEN', 'FANDEIN', 'FANELY', 'FAR', 'FARMER', 'FASHION', 'FAVOR', 'FAVORITE', 'FEALS', 'FEARED', 'FEASERCHIP', 'FEATURE', 'FED', 'FEEL', 'FEELS', 'FEERED', 'FEILD', 'FELLOW', 'FEMALE', 'FEMES', 'FENCE', 'FERTALL', 'FERTILE', 'FEWER', 'FICRORY', 'FIGURES', 'FILDS', 'FILE', 'FILLORT', 'FILM', 'FIMLATION', 'FINANCES', 'FINANCIAL', 'FINCING', 'FINGER', 'FINISH', 'FINTEN', 'FIRM', 'FIRMLY', 'FIRMS', 'FIRR', 'FISHING', 'FISTENTS', 'FLAVES', 'FLEW', 'FLIED', 'FLIGHT', 'FLIPER', 'FLITE', 'FLIYL', 'FLOJEN', 'FLOOKER', 'FLOOKING', 'FLOWER', 'FLOWS', 'FLUING', 'FLYLY', 'FOCUS', 'FOLLOWS', 'FONOS', 'FOODBACE', 'FOOMILY', 'FOOTBALL', 'FORDOSTAN', 'FORELY', 'FORGOTTEN', 'FORMAL', 'FORMATION', 'FORMED', 'FORMER', 'FORMING', 'FORNEL', 'FOSTING', 'FRAME', 'FRAPE', 'FREAT', 'FREEN', 'FRIENDLY', 'FRIGHTENED', 'FRINKS', 'FROZEN', 'FRUIDELY', 'FRUIT', 'FUEL', 'FULLY', 'FUNCTIONS', 'FUNNY', 'FUR', 'FURLORY', 'FURNINISE', 'FURNITURE', 'FUS', 'FUSSON', 'FUTICAL', 'GADELY', 'GAIN', 'GAINED', 'GAMES', 'GANERS', 'GASES', 'GASS', 'GATE', 'GATHER', 'GATHERED', 'GAVED', 'GAWLED', 'GAYES', 'GEDDED', 'GENERATION', 'GENTLE', 'GERMAN', 'GERRY', 'GIFTEN', 'GIVING', 'GLANCE', 'GOAL', 'GOALS', 'GOLDEN', 'GON', 'GOOD', 'GOUL', 'GOVERNOR', 'GRABBED', 'GRACKHAQUER', 'GRACKROILER', 'GRADE', 'GRAIN', 'GRAMP', 'GRAND', 'GRANDFATHER', 'GRANDMOTHER', 'GRANGED', 'GRANT', 'GRANTED', 'GRAY', 'GREAM', 'GRID', 'GRONE', 'GROUP', 'GROWS', 'GU', 'GUARD', 'GUAVE', 'GUDMAN', 'GUIDE', 'GUITS', 'GUN', 'GUNDLE', 'GURES', 'GW', 'HABIT', 'HAGIL', 'HANDED', 'HANGING', 'HAPPENING', 'HAPPINESS', 'HAPS', 'HARDER', 'HARM', 'HARMFUL', 'HARTTUL', 'HASAN', 'HAT', 'HAVEN', 'HAWL', 'HEADED', 'HEARING', 'HEAVILY', 'HEIGHT', 'HEILED', 'HEINING', 'HELKEST', 'HELPFUL', 'HERTTUL', 'HIDE', 'HIDES', 'HIGHEST', 'HIME', 'HINES', 'HIRE', 'HIRED', 'HOESED', 'HOINS', 'HOLDS', 'HOLE', 'HOLES', 'HOMMER', 'HONOR', 'HONT', 'HOTCH', 'HOTS', 'HOUCHHOGS', 'HOUSEHOLD', 'HUD', 'HUET', 'HUMAN', 'HUMANS', 'HUMPY', 'HUNENS', 'HUNT', 'HURRY', 'HYDROGEN', 'I', 'IBBLARITY', 'IDEAS', 'IDENTIFIED', 'IDMORENTLY', 'IDTHILATION', 'ILELEIN', 'ILEW', 'ILL', 'ILLNESS', 'ILLUSTRATION', 'ILSHUSSION', 'IMAGE', 'IMBECT', 'IMBRIVED', 'IMEPY', 'IMMEDIATE', 'IMPACT', 'IMPLICATIONS', 'IMPRESSION', 'IMPROVE', 'IMPROVED', 'IN', 'INCH', 'INCHIEVINTLY', 'INCHROSTIONS', 'INCREASINGLY', 'INDEGAUR', 'INDERCOTIALAL', 'INDICATE', 'INDOMBLIES', 'INDUSTRIES', 'INFLUENCE', 'INFLUENCED', 'INFORANTS', 'INGENCE', 'INITIATE', 'INLISTED', 'INNER', 'INSECT', 'INSECTS', 'INSPIRE', 'INSTITUTIONS', 'INSTRUCATE', 'INSTRUCTIONS', 'INSTRUMENT', 'INSURANCE', 'INTENDED', 'INTERIOR', 'INTERNAL', 'INTERNATIONAL', 'INTRODUCED', 'INTROFORDS', 'INTUITIONS', 'INVENTED', 'INVENTION', 'INVIGNS', 'INVOLVE', 'IPAYS', 'IPONTIHOOD', 'IRRYRTRATION', 'ISBACKS', 'ISLAND', 'ISLANDS', 'ISSUES', 'ISTURN', 'IT', 'ITALIAN', 'ITEM', 'JALLOES', 'JAPANESE', 'JECANERN', 'JEERNEM', 'JICAL', 'JOIN', 'JOK', 'JOSTIME', 'JOURNEY', 'JOY', 'JUDGE', 'JUDY', 'JUFFS', 'JULT', 'JUMP', 'JUSSELS', 'JUSTICE', 'KEEDS', 'KEEPS', 'KID', 'KIDES', 'KINGDOM', 'KINGS', 'KINGTUM', 'KNEES', 'KNOUS', 'KOD', 'LABORATORY', 'LAIRE', 'LAKES', 'LAMIL', 'LANDED', 'LANGER', 'LANGUAGE', 'LARGE', 'LARGELY', 'LAST', 'LATIN', 'LATTER', 'LAUGH', 'LAW', 'LAWED', 'LAYER', 'LEADERSHIP', 'LEADS', 'LEAMED', 'LEANED', 'LEANING', 'LEARS', 'LEATHER', 'LECER', 'LEESE', 'LEG', 'LEGAL', 'LELLAW', 'LENNY', 'LEPS', 'LER', 'LESSON', 'LESSONS', 'LETTERS', 'LIBELABLES', 'LIBLE', 'LIBRARY', 'LIFT', 'LIKES', 'LIMIT', 'LINANDIEL', 'LINED', 'LINER', 'LINTS', 'LIPS', 'LIRK', 'LISTED', 'LISTENED', 'LISTUE', 'LITERATURE', 'LIVELY', 'LOAD', 'LOCATED', 'LOCATION', 'LOIL', 'LOMIN', 'LONED', 'LONELY', 'LOOD', 'LOOSE', 'LOOSTER', 'LORD', 'LORDS', 'LORMER', 'LOTS', 'LOVELY', 'LOVEY', 'LOVILY', 'LOWANDS', 'LUCK', 'LUNED', 'LUNGS', 'LUNS', 'LYSTODEN', 'MACHINE', 'MACHINERY', 'MACING', 'MACMENT', 'MAD', 'MADERS', 'MADISITION', 'MAGE', 'MAGIC', 'MAIL', 'MAINLY', 'MALE', 'MAME', 'MAMED', 'MAMES', 'MAMIETOUS', 'MANAGED', 'MANUFACTURING', 'MAP', 'MAPS', 'MARALTS', 'MARKS', 'MARRIAGE', 'MARROUDS', 'MARSIES', 'MAS', 'MASSARD', 'MATCH', 'MATTERS', 'MAXIMUM', 'MAYERENCE', 'MAYOR', 'MEAL', 'MEALS', 'MEASURES', 'MECHANICAL', 'MECHANICALS', 'MEDICINE', 'MEDIUM', 'MEDOATIONS', 'MEEGENABLE', 'MEEL', 'MEMIEITLY', 'MEMORY', 'MENTAL', 'MENTIERES', 'MENTIONED', 'MERANITY', 'MERCHANT', 'MERCHANTS', 'MERICTION', 'MERSHANDS', 'MESSAGE', 'METAL', 'METALS', 'METS', 'MIDE', 'MIFFERED', 'MIKED', 'MILE', 'MIMICIES', 'MINDS', 'MINERALS', 'MINIMUM', 'MINISEY', 'MINISTER', 'MINOR', 'MINUTE', 'MISREAD', 'MISSING', 'MISTAKE', 'MISTICS', 'MISYR', 'MITHE', 'MIXED', 'MIXTURE', 'MNERIMMERISTIC', 'MOBRALERY', 'MOCACATED', 'MOLLING', 'MOM', 'MONEMENED', 'MONEY', 'MOR', 'MORELY', 'MORSION', 'MOTOR', 'MOUGH', 'MOULURES', 'MOVEMENTS', 'MOVIES', 'MUD', 'MURCUSES', 'MURMIT', 'MUSCLE', 'MUSCLES', 'MUTTLE', 'MUZES', 'NAITOUS', 'NALICS', 'NALITED', 'NATIVE', 'NATURAL', 'NATURALLY', 'NEDED', 'NEGATIVE', 'NEIGHBOR', 'NEIGHBORHOOD', 'NEIGHBORS', 'NELLAKES', 'NERDELLY', 'NERVOUS', 'NEWS', 'NEWSPAPERS', 'NICEROES', 'NIGHT', 'NIGHTS', 'NIMMED', 'NISIGRA', 'NISTOAR', 'NODDED', 'NODDLE', 'NOMED', 'NOON', 'NOOP', 'NORMALLY', 'NOTED', 'NOTES', 'NUCED', 'NUCLEAR', 'NUMEROUS', 'NUPATISM', 'NURSE', 'NUTRIENTS', 'OAMLIERS', 'OAREN', 'OBATION', 'OBSERVATION', 'OBTAINED', 'OBVIOUS', 'OCCASIONALLY', 'OCCERSED', 'OCCICIEL', 'OCCUPIED', 'OCCURING', 'OCCURRED', 'OCEANS', 'OCTUCES', 'OCTULIRATIONS', 'ODD', 'OEMEBEANS', 'OFFICER', 'OFFICES', 'OFFICIAL', 'OLDEST', 'OMDONISM', 'ONAGRA', 'ONSCIBETIONS', 'ONX', 'OPERATIONS', 'OPINION', 'OPPAKES', 'OPPINION', 'OPPORTUNITIES', 'OPPOSED', 'OPPOSITE', 'OPPRTYUNITIES', 'ORANGE', 'ORDERS', 'ORDINS', 'ORGANISEM', 'ORGANISM', 'ORGANISMS', 'ORGANIZATIONS', 'ORGANS', 'ORGASIM', 'ORLESCUNITIES', 'ORLUGUINALLY', 'ORUBEAL', 'OSBAINED', 'OUGHT', 'OUSED', 'OUT', 'OUTER', 'OUTHAT', 'OUTPUT', 'OUTSIDE', 'OVEINS', 'OVERFLOW', 'OWBAN', 'OWNER', 'PACKED', 'PADE', 'PAINT', 'PAIRLY', 'PAITS', 'PALE', 'PAPERS', 'PARACLEGM', 'PARAGRAPH', 'PARENT', 'PARENTS', 'PARIENE', 'PARTIES', 'PARTLY', 'PASSAGE', 'PASSING', 'PATIENT', 'PATIENTLY', 'PAVED', 'PAYIC', 'PAYING', 'PAYMENT', 'PEARTES', 'PECTORS', 'PEETLY', 'PEFLINILAL', 'PENCIL', 'PENGOL', 'PEOPLE', 'PEOPLES', 'PERFECTLY', 'PERFORMANCE', 'PERIODS', 'PERMANENT', 'PERMIT', 'PERSONALITY', 'PERSPECTIVE', 'PERVAINLY', 'PERVARRANCE', 'PESTING', 'PETTUTION', 'PEZEN', 'PHITTERED', 'PHONE', 'PHOTERS', 'PHYCROCESICAL', 'PILE', 'PILELTS', 'PIND', 'PINE', 'PINK', 'PINTING', 'PIRT', 'PIST', 'PITICINE', 'PLAILS', 'PLAIN', 'PLAINS', 'PLAKE', 'PLANE', 'PLANET', 'PLANS', 'PLANTED', 'PLASTIC', 'PLATE', 'PLAYS', 'PLEASANT', 'PLEASED', 'PLEASURE', 'PLIANTIRS', 'PLOW', 'PLOWEN', 'POCKET', 'POLE', 'POLICIES', 'POLISH', 'POLITICS', 'POLKS', 'POLLUTION', 'POLMETARY', 'POND', 'POOL', 'POORED', 'POOTILY', 'POOTS', 'POPID', 'PORCH', 'POROR', 'PORT', 'PORTION', 'POSSIBILITY', 'POSSIBLY', 'POST', 'POTE', 'POTENTIAL', 'POUL', 'POUNDS', 'POUR', 'POURED', 'POUTES', 'POWER', 'PRACTICAL', 'PRACTICES', 'PRARCIGAL', 'PREBIT', 'PRECH', 'PREDRESS', 'PREET', 'PREFECTLY', 'PREPARATION', 'PRESDIENT', 'PRESENDENT IAL', 'PRESIDENTIAL', 'PRESISE', 'PRESS', 'PRETERSIES', 'PREVIOUS', 'PREW', 'PRIDE', 'PRIMARILY', 'PRINCIPAL', 'PRINCIPLE', 'PRINNIGNA', 'PRINT', 'PRIVE', 'PROBOLLS', 'PROCEDURE', 'PROCEFAGE', 'PROCESSING', 'PRODE', 'PRODELATION', 'PRODUCED', 'PRODUCING', 'PROFFIC', 'PROFIT', 'PROGRAM', 'PROGRESS', 'PROJECT', 'PROJIVE', 'PROMISE', 'PROMISHING', 'PROOD', 'PROPERTIES', 'PROPOSED', 'PRORIDENTEER', 'PROSOMING', 'PROTECTED', 'PROTOGING', 'PROUD', 'PROVE', 'PROVIDING', 'PRUCENILY', 'PRURTIGES', 'PRUTLICAL', 'PSYCHOLOGICAL', 'PUBLISHED', 'PUCKED', 'PULLING', 'PUNE', 'PUPPIFICANT', 'PURCHASE', 'PURE', 'PURPOSES', 'PURSHARE', 'PUSHING', 'PUSLIPPED', 'QUANTITY', 'QUARTER', 'QUEAT', 'QUEEN', 'QUIETLY', 'RAD', 'RAGGEST', 'RAILROAD', 'RAILSOUD', 'RAISING', 'RALES', 'RANDOM', 'RANTENTES', 'RAPID', 'RAPIDLY', 'RAPPER', 'RAR', 'RARELY', 'RARERALS', 'RASSING', 'RATES', 'RAW', 'RAX', 'RAYS', 'REACHES', 'REACTION', 'READER', 'READILY', 'REAF', 'REALITY', 'REALIZE', 'REASONABLE', 'REBOILING', 'REBOLES', 'RECALE', 'RECALL', 'RECLEPENTATOPES', 'RECOGNIZE', 'RECORDED', 'REDOILIC', 'REDUCE', 'REEPSION', 'REESICK', 'REFERENCE', 'REFLECT', 'REFOILED', 'REGARDED', 'REGOCRIZE', 'REGRESHMENTS', 'REGURT', 'REINFORSMENT', 'RELALAGE', 'RELATIONS', 'RELATIONSHIP', 'RELATIONSHIPS', 'RELATIVE', 'RELEASE', 'RELENSING', 'RELIEF', 'RELIGION', 'REMAINING', 'REMARKABLE', 'REMEMBER', 'REMERSED', 'REMOVE', 'REPEATED', 'REPELL', 'REPLACE', 'REPLACED', 'REPORT', 'REPORTS', 'REPRESENTATIVES', 'REPUBLIC', 'REQUIREMENTS', 'REREARE', 'REROOF', 'RESENTANTS', 'RESIONED', 'RESISTANCE', 'RESPECK', 'RESPOND', 'RESPONSIBILITY', 'RESTERN', 'RESULTING', 'RESULTS', 'RETRALL', 'REVATIONGLEDE', 'REVOCT', 'REW', 'REWARD', 'RHONE', 'RID', 'RIDING', 'RIGH', 'RIGHT', 'RING', 'RINT', 'RISES', 'RISHY', 'RISK', 'ROAT', 'ROCKY', 'RODE', 'RODEN', 'ROLING', 'ROLL', 'ROMAN', 'ROMBER', 'ROMER', 'RONG', 'ROOBLE', 'ROOF', 'ROOMS', 'ROORS', 'ROOTER', 'ROPE', 'ROSSOON', 'ROTALS', 'ROUGH', 'ROULE', 'ROULETTE', 'ROUNGED', 'ROUTE', 'ROW', 'ROYAL', 'RUBBER', 'RUDS', 'RUFTLY', 'RULER', 'RULLAR', 'RUN', 'RUNATE', 'RUNS', 'RUNTAL', 'RUNY', 'RUP', 'RUSH', 'RUSSAGE', 'RUSSIAN', 'RUSSIANS', 'RUTTERS', 'RUZAL', 'SAD', 'SAFFER', 'SAIL', 'SAIN', 'SALE', 'SALES', 'SAMELY', 'SANCE', 'SANENT', 'SANGORALITY', 'SAPE', 'SATENTIEL', 'SATILVINTION', 'SATISFACTION', 'SAUBREMENT', 'SAULING', 'SAVED', 'SAXTURE', 'SCATTERED', 'SCENE', 'SCESH', 'SCHIT', 'SCIENTIST', 'SCREAN', 'SCREEN', 'SEADS', 'SEAK', 'SEAS', 'SEASON', 'SECIOME', 'SECONDS', 'SECRETARY', 'SECTIONS', 'SECURITY', 'SEEBON', 'SEEDS', 'SEEK', 'SEGODES', 'SELECTION', 'SELLING', 'SEMITICS', 'SENATE', 'SENTANCES', 'SENTENCES', 'SENTERS', 'SEPARATED', 'SEPHEGNITILITY', 'SERIOUSLY', 'SESIRE', 'SESIUP', 'SESTANENT', 'SESTS', 'SETNAL', 'SETS', 'SETTLE', 'SETTLEMENT', 'SEVERE', 'SEX', 'SHACK', 'SHADLE', 'SHADOW', 'SHALING', 'SHANGS', 'SHAPES', 'SHARED', 'SHARPLY', 'SHEALMERS', 'SHECKED', 'SHEDICAL', 'SHEEP', 'SHEET', 'SHELL', 'SHELTER', 'SHERT', 'SHIGES', 'SHINDING', 'SHINED', 'SHINETE', 'SHINING', 'SHINY', 'SHIRT', 'SHIRTLY', 'SHOEP', 'SHOLL', 'SHORE', 'SHOULDER', 'SHOULDERS', 'SHOWING', 'SHURE', 'SIED', 'SIGHED', 'SIGNAL', 'SIGNIFICANT', 'SILENCE', 'SILKED', 'SING', 'SININDER', 'SINT', 'SIRTIONS', 'SISTER', 'SISTERS', 'SITUATIONS', 'SIZES', 'SKILLED', 'SKISHED', 'SLANE', 'SLAVE', 'SLAVERY', 'SLAVES', 'SLEASING', 'SLEEPING', 'SLICKED', 'SLIGHT', 'SLIPPED', 'SLOW', 'SMALLEST', 'SMESING', 'SMILE', 'SMILING', 'SMONGEST', 'SO', 'SOCIETIES', 'SODE', 'SOFT', 'SOFTLY', 'SOIRS', 'SOLL', 'SOLORY', 'SOLVE', 'SONG', 'SOPE', 'SORRY', 'SOSCLE', 'SOUGHT', 'SOUL', 'SOUNDED', 'SOUS', 'SOUT', 'SPANCED', 'SPAND', 'SPARET', 'SPEAKER', 'SPECIALIZED', 'SPEDIT', 'SPEETURE', 'SPENDING', 'SPHISSMAS', 'SPHISTEIN', 'SPIGHT', 'SPIRIT', 'SPITE', 'SPLIT', 'SPOKEN', 'SPORTS', 'SPOSED', 'SPOSTIC', 'SPOSTING', 'SPOWS', 'SPREAD', 'STABLE', 'STACH', 'STADICALS', 'STAFF', 'STAGES', 'STAIRS', 'STAITS', 'STAMEMENED', 'STAND', 'STANDARDS', 'STANDS', 'STANES', 'STANNACKS', 'STAR', 'STARIS', 'STARKS', 'STARTS', 'STATE', 'STATED', 'STATEMENT', 'STATEMENTS', 'STATUS', 'STAVECTED', 'STAW', 'STEADY', 'STEAM', 'STEAR', 'STECENCOUS', 'STECIEES', 'STECK', 'STOCK', 'STOLL', 'STOMACH', 'STONACTERS', 'STONES', 'STOOTY', 'STOPAPE', 'STOPED', 'STORM', 'STOWL', 'STREAM', 'STREEM', 'STRESS', 'STRETCH', 'STRIKE', 'STRING', 'STRINKER', 'STRINT', 'STRITE', 'STRONG', 'STRONGER', 'STROTCH', 'STRUCTURE', 'STRUCTURES', 'STRUDDLE', 'STRUGGLE', 'STRULLER', 'STUCK', 'STUDIED', 'STUDY', 'STUFF', 'STULT', 'SUCCESS', 'SUCKET', 'SUFFERED', 'SUFFICIENT', 'SUGGEST', 'SUIT', 'SUMBERTED', 'SUMBICOUNT', 'SUNURECTERING', 'SUOCIDE', 'SUPPER', 'SUPPORTED', 'SUPREME', 'SUPROCT', 'SURE', 'SURELY', 'SURFACES', 'SURROUNDING', 'SURVIVE', 'SURVORN', 'SURVOWES', 'SURVUVE', 'SUSCIBLY', 'SUSH', 'SUTTOUNTING', 'SUVIDION', 'SUX', 'SUXISUM', 'SWANE', 'SWEAM', 'SWEET', 'SWIM', 'SYNNIRILITY', 'SYTEM', 'TABER', 'TACTS', 'TAISTLY', 'TANE', 'TANISH', 'TAREURE', 'TASHED', 'TASIK', 'TASK', 'TASKS', 'TASTE', 'TAULER', 'TAULING', 'TAWING', 'TAWNS', 'TAX', 'TAYS', 'TEA', 'TEACH', 'TEACHED', 'TEALS', 'TEAR', 'TEARS', 'TECHNIQUE', 'TECHNOLOGY', 'TEEL', 'TEERS', 'TEETURE', 'TEFAL', 'TEMACS', 'TEMPENING', 'TEMPERATURES', 'TENTNIGNS', 'TEP', 'TEPERTURE', 'TERRITORY', 'TESTMALOMY', 'TESTS', 'TEXTBOOK', 'TEXTURE', 'THAT', 'THE', 'THINKS', 'THIS', 'THOUGHT', 'THOUGHTS', 'THRAW', 'THROAT', 'THROUT', 'THROW', 'TIED', 'TIGHS', 'TIGHT', 'TIME', 'TINELY', 'TIP', 'TISSUE', 'TISSUES', 'TITHED', 'TITLE', 'TO', 'TOLLY', 'TOM', 'TONE', 'TONGUE', 'TOOL', 'TOPIC', 'TORCED', 'TORTLY', 'TOS', 'TOU', 'TOUCHED', 'TOUNT', 'TOWARDS', 'TRACK', 'TRADING', 'TRADITIONAL', 'TRAFFIC', 'TRAIL', 'TRAINED', 'TRALLETTE', 'TRANS', 'TRANSPORTATION', 'TRANSPOTATION', 'TRATHMOLLATION', 'TRAUNTS', 'TRAVEL', 'TRAVELED', 'TRAZE', 'TREATMENT', 'TREEPS', 'TREMENDOUS', 'TREW', 'TRIAL', 'TRIBE', 'TRIBES', 'TRIGHS', 'TRIST', 'TROOPS', 'TRUCK', 'TRUDS', 'TRULY', 'TRUST', 'TUBE', 'TUED', 'TUMIC', 'TURETIONS', 'TYMOCATOGY', 'TYPED', 'TYPICAL', 'UDALATIONS', 'ULBET', 'UNABLE', 'UNASTE', 'UNIFORM', 'UNIPORLD', 'UNIQUE', 'UNISAUR', 'UNIVERSE', 'UNKNOWN', 'UNSCORM', 'UNSER', 'UNTEST', 'UNUSUAL', 'UNUSUSAL', 'UPSET', 'UPTUPIED', 'URALTS', 'URBAN', 'URMERS', 'URNER', 'URTNESS', 'USMERSATION', 'USPICER', 'UTMIOUS', 'VALLEYS', 'VALUABLE', 'VANDERCUL', 'VAVERPOR', 'VEGETABLES', 'VELTENIA', 'VESSELS', 'VICTORY', 'VIELS', 'VIEWS', 'VILAGES', 'VILLAGES', 'VISIBLE', 'VISITED', 'VITAL', 'VOICES', 'VOLUME', 'VOSULL', 'VOTING', 'VULKES', 'VUWRIENCE', 'WAGES', 'WAGON', 'WAMS', 'WANG', 'WANT', 'WANTER', 'WARS', 'WARTER', 'WAS', 'WASH', 'WASTE', 'WASTES', 'WATERS', 'WAUNCH', 'WAVE', 'WEALTH', 'WEAPON', 'WEAPONS', 'WEAREN', 'WEARING', 'WEARNT', 'WEATHER', 'WEMPER', 'WERN', 'WHEAT', 'WHEEL', 'WHISPERED', 'WHISPERING', 'WHOOL', 'WIDELY', 'WIDER', 'WILL', 'WIMP', 'WIMPS', 'WIMS', 'WIN', 'WIND', 'WINDS', 'WINED', 'WING', 'WINGS', 'WIRE', 'WIREPAPERS', 'WIRMORY', 'WISE', 'WIXON', 'WOLVE', 'WONDERFUL', 'WOODEN', 'WOOMONS', 'WOOTING', 'WORD', 'WORKER', 'WORN', 'WORRY', 'WORST', 'WRANCE', 'WRAPPED', 'WRIPPED', 'WRITERS', 'WROMITIENAL', 'YARDS', 'YEASTES', 'YELLED', 'YOUNGER', 'YOUTH', 'YTHMS']


class MemoryExperiment:
    """Cox, Hemmer, Aue & Criss (2018), "Information and processes underlying semantic and
    episodic memory across tasks, items, and individuals", JEP: General, 147(4), 545-590.

    Design (Method / Experiment, pp. 545-549): a single study with 15 study/test blocks.
    The first 5 blocks present each of the five tasks once (random order); the remaining 10
    present all five tasks twice (random order), so each task appears three times. Study
    blocks (all tasks except lexical decision) show 20 word pairs side by side (2 s each),
    each followed by a self-paced 1-9 association rating, then a 45-s digit-addition
    distractor, then the test. Lexical decision has no study phase.

    Test counts per block (paper p. 546-547): associative recognition 20 pairs (10 intact +
    10 rearranged), single-item recognition 20 items (10 old + 10 foils), cued recall 20 cues
    (one word per studied pair), lexical decision 20 letter strings (10 words + 10
    pseudowords), free recall = the participant's recalled words.

    ASSUMPTION: free recall is modelled as one row per studied word (each recalled or
    reported as not recalled, resp.type Miss), since the transcripts narrate each studied
    word in the block; real free-recall blocks also include some extra-list intrusions, which
    this simulator omits.

    ASSUMPTION: stimuli are sampled uniformly from the word pool recovered from the repo's
    ``exp0.csv`` (``stim.string.left``/``right`` plus uppercase ``resp.string``), which mixes
    real words with lexical pseudowords. Sampling is without replacement within a participant
    across blocks (paper: "sampled ... without replacement ... no items repeated between
    blocks").

    ASSUMPTION: columns a text simulator cannot produce are dropped: ``rt``, item-frequency /
    context-variability / OLD20 / K-F columns, numeric stimulus codes, study-position and study
    partner columns, and the post-hoc ``recall.type`` / ``resp.type.rescore``
    classifications. The kept columns mirror ``exp0.csv`` (same names, dtypes, coding).
    """

    def __init__(self):
        self.name = "cox_2018_information_exp0"
        self.word_pool = list(WORDS)
        self.num_blocks = 15
        self.num_study_pairs = 20
        self.num_test_items = 20
        self.rating_digits = [str(i) for i in range(1, 10)]

    def _task_order(self):
        # first 5 blocks = one of each task (random); next 10 = each task twice (random)
        first = list(range(5))
        random.shuffle(first)
        rest = list(range(5)) * 2
        random.shuffle(rest)
        return first + rest

    def _draw(self, used, k):
        pool = [w for w in self.word_pool if w not in used]
        random.shuffle(pool)
        drawn = pool[:k]
        used.update(drawn)
        return drawn

    def _study_pairs(self, used):
        words = self._draw(used, self.num_study_pairs * 2)
        return [(words[i], words[i + 1]) for i in range(0, len(words), 2)]

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            rng = random.Random()
            used = set()
            task_occur = {t: 0 for t in range(5)}
            prompt = INTRO
            for bi, task_id in enumerate(self._task_order()):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                bs = bi + 1
                block = task_occur[task_id]
                task_occur[task_id] += 1
                prompt += f"\nBlock {bs}: {TASK_NAMES[task_id]}."
                study_pairs = None
                if task_id != 3:
                    study_pairs = self._study_pairs(used)
                    for pi, (a, b) in enumerate(study_pairs):
                        pair = f"{a} {b}".strip()
                        prompt += (f"\nYou study the word pair {pair}. You rate how associated "
                                   f"the two words are (1-9): [HUMAN_RESPONSE]")
                        rating = agent(prompt, choice_options=self.rating_digits)
                        prompt += f"{rating}[/HUMAN_RESPONSE]."
                        rows.append({"participant_id": participant, "trial": 0,
                                     "task_id": task_id, "block": block, "phase": "study",
                                     "condition": CONDITION[task_id], "trial_in_block": pi + 1,
                                     "block_source": bs, "stim.string.left": a,
                                     "stim.string.right": b, "stim.distractor": 0,
                                     "studied": 0, "distractor.resp": 0, "response": int(rating),
                                     "resp.string": np.nan, "resp.type": np.nan})
                prompt += f"\n{TEST_INSTR[task_id]}"
                if task_id == 2:
                    flat = [w for pair in study_pairs for w in pair]
                    for wi, w in enumerate(flat):
                        if w:
                            prompt += "\nYou type [HUMAN_RESPONSE]"
                            recall = agent(prompt, choice_options=None)
                            if recall and recall.strip():
                                prompt += f"{recall}[/HUMAN_RESPONSE]."
                                rows.append({"participant_id": participant, "trial": 0,
                                             "task_id": task_id, "block": block, "phase": "test",
                                             "condition": CONDITION[task_id],
                                             "trial_in_block": wi + 1, "block_source": bs,
                                             "stim.string.left": np.nan, "stim.string.right": np.nan,
                                             "stim.distractor": 0, "studied": 1,
                                             "distractor.resp": 0, "response": 1,
                                             "resp.string": recall, "resp.type": "Hit"})
                            else:
                                prompt = prompt.rsplit("\nYou type [HUMAN_RESPONSE]", 1)[0]
                                prompt += f"\nYou do not recall {w.upper()}."
                                rows.append({"participant_id": participant, "trial": 0,
                                             "task_id": task_id, "block": block, "phase": "test",
                                             "condition": CONDITION[task_id],
                                             "trial_in_block": wi + 1, "block_source": bs,
                                             "stim.string.left": np.nan, "stim.string.right": np.nan,
                                             "stim.distractor": 0, "studied": 1,
                                             "distractor.resp": 0, "response": 0,
                                             "resp.string": w, "resp.type": "Miss"})
                        else:
                            prompt += "\nYou type a word that was not on the list."
                            rows.append({"participant_id": participant, "trial": 0,
                                         "task_id": task_id, "block": block, "phase": "test",
                                         "condition": CONDITION[task_id],
                                         "trial_in_block": wi + 1, "block_source": bs,
                                         "stim.string.left": np.nan, "stim.string.right": np.nan,
                                         "stim.distractor": 0, "studied": 0, "distractor.resp": 0,
                                         "response": 1, "resp.string": np.nan, "resp.type": np.nan})
                elif task_id == 1:
                    for ci, (a, b) in enumerate(study_pairs):
                        cue, _ = (a, b) if rng.random() < 0.5 else (b, a)
                        prompt += f"\nCue: {cue}. You type [HUMAN_RESPONSE]"
                        recall = agent(prompt, choice_options=None)
                        if recall and recall.strip():
                            prompt += f"{recall}[/HUMAN_RESPONSE]."
                            rows.append({"participant_id": participant, "trial": 0,
                                         "task_id": task_id, "block": block, "phase": "test",
                                         "condition": CONDITION[task_id], "trial_in_block": ci + 1,
                                         "block_source": bs, "stim.string.left": cue,
                                         "stim.string.right": np.nan, "stim.distractor": 0,
                                         "studied": 1, "distractor.resp": 0, "response": 1,
                                         "resp.string": recall, "resp.type": "Hit"})
                        else:
                            prompt = prompt.rsplit("You type [HUMAN_RESPONSE]", 1)[0]
                            prompt += "You do not recall the partner word."
                            rows.append({"participant_id": participant, "trial": 0,
                                         "task_id": task_id, "block": block, "phase": "test",
                                         "condition": CONDITION[task_id], "trial_in_block": ci + 1,
                                         "block_source": bs, "stim.string.left": cue,
                                         "stim.string.right": np.nan, "stim.distractor": 0,
                                         "studied": 1, "distractor.resp": 0, "response": 0,
                                         "resp.string": np.nan, "resp.type": "Miss"})
                else:
                    for ti in range(self.num_test_items):
                        if task_id == 0:
                            if ti < 10:
                                a, b = study_pairs[ti]
                                studied = 1
                                prompt += f"\nYou see the pair {a} {b}. Is this pair intact from study? [HUMAN_RESPONSE]"
                            else:
                                a, b = study_pairs[ti][0], study_pairs[(ti - 10 + 3) % 10][1]
                                studied = 0
                                prompt += f"\nYou see the pair {a} {b}. Is this pair intact from study? [HUMAN_RESPONSE]"
                        elif task_id == 4:
                            if ti < 10:
                                a = study_pairs[ti][0 if rng.random() < 0.5 else 1]
                                studied = 1
                            else:
                                a = self._draw(used, 1)[0]
                                studied = 0
                            prompt += f"\nYou see the word {a}. Was it on the list you just studied? [HUMAN_RESPONSE]"
                        else:  # lexical decision
                            a = self._draw(used, 1)[0]
                            studied = 0
                            prompt += f"\nYou see the letter string {a}. Is it a word? [HUMAN_RESPONSE]"
                        token = agent(prompt, choice_options=["Y", "N"])
                        resp = 1 if token == "Y" else 0
                        prompt += f"{token}[/HUMAN_RESPONSE]"
                        rows.append({"participant_id": participant, "trial": 0,
                                     "task_id": task_id, "block": block, "phase": "test",
                                     "condition": CONDITION[task_id], "trial_in_block": ti + 1,
                                     "block_source": bs, "stim.string.left": a,
                                     "stim.string.right": (b if task_id == 0 else np.nan),
                                     "stim.distractor": 0, "studied": studied,
                                     "distractor.resp": 0, "response": resp,
                                     "resp.string": np.nan, "resp.type": np.nan})
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=COLS)
        df["trial"] = df.groupby(["participant_id", "task_id"]).cumcount()
        return df, prompts


def _random_agent(prompt, choice_options=None):
    if choice_options is None:
        return None if np.random.rand() < 0.5 else "recalled"
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
        random.seed(args.seed)

    task = MemoryExperiment()
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