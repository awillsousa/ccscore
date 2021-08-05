from os import path, getenv
from dotenv import load_dotenv

# Load config file
load_dotenv(path.join(path.dirname(__file__), "ccscore.conf"))

DBPEDIA_SCRIPT = getenv("DBPEDIA_SCRIPT")
DBPEDIA_IP = getenv("DBPEDIA_IP")
DBPEDIA_PORT = getenv("DBPEDIA_PORT")
TEP2_PATH = getenv("TEP2_PATH")
COGROO_DIR = getenv("COGROO_DIR")
COGROO_SCRIPT = getenv("COGROO_SCRIPT")
USE_CORREF = getenv("USE_CORREF")

# Errors from CoGrOO grammatical revisor that are related with
# lexical cohesion problems
ERROS_COGROO_IAC = ['government:GOVERNMENT',
                    'probs:paronyms',
                    'xml:61',
                    'xml:65',
                    'xml:67',
                    'xml:71',
                    'xml:73',
                    'xml:97']

# Errors from GoGrOO grammatical revisor that are related with
# form and structure problems
ERROS_COGROO_IPR = ['xml:1', 'xml:2', 'xml:3', 'xml:4', 'xml:5',
                    'xml:6', 'xml:9', 'xml:10', 'xml:11', 'xml:12',
                    'xml:13', 'xml:14', 'xml:17', 'xml:21', 'xml:39',
                    'xml:40', 'xml:42', 'xml:46', 'xml:47', 'xml:50',
                    'xml:51', 'xml:52', 'xml:57', 'xml:58', 'xml:75',
                    'xml:78', 'xml:79', 'xml:80', 'xml:82', 'xml:84',
                    'xml:86', 'xml:87', 'xml:88', 'xml:91', 'xml:94',
                    'xml:95', 'xml:96', 'xml:103', 'xml:104', 'xml:105',
                    'xml:106', 'xml:107', 'xml:110', 'xml:111', 'xml:112',
                    'xml:113', 'xml:114', 'xml:115', 'xml:117', 'xml:118',
                    'xml:121', 'xml:122', 'xml:124', 'xml:127', 'xml:128',
                    'xml:129']
