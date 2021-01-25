from os import path, getenv
from dotenv import load_dotenv

# Load config file
load_dotenv(path.join(path.dirname(__file__), "ccscore.conf"))

DBPEDIA_IP = getenv("DBPEDIA_IP")
DBPEDIA_PORT = getenv("DBPEDIA_PORT")
