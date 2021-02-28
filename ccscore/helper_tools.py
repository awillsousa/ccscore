import requests
import confapp as config
from cogroo_interface import Cogroo
from tep2 import GrupoSinonimo
from bs4 import BeautifulSoup
import requests
import pickle
import tep2
import re


# Endpoint DBPedia
URL_REST_DBPEDIA = "http://{}:{}/rest/annotate".format(
                    config.DBPEDIA_IP,
                    config.DBPEDIA_PORT)


dic_tep2 = None
with open(config.TEP2_PATH, 'rb') as f:
    dic_tep2 = pickle.load(f)


def get_dbpedia_entries(text, formated=True, 
                        url=URL_REST_DBPEDIA,
                        confidence=0.35,
                        policy='blacklist'):
    """
    Get entities mentions by calling a DBpedia Spotlight REST API

    :param text: Text to be analyzed
    :param url: endpoint to annotate text
    """

    # params to rest call 
    PARAMS = {'confidence':confidence, 'text': text, 'policy': policy} 

    # send request 
    r = requests.get(url = url, params = PARAMS, headers={'Accept': "application/json"}) 

    # Get result in json format 
    result = r.json() 
    if formated:
        return format_dbpedia_result(result)

    return result


def format_dbpedia_result(result):
    """
    Convert the json result obtained from DBpedia Spolight Endpoint
    into a dictionary

    :param result: json result of a request call 
    """    
    if 'Resources' in result.keys():
        return  {ent['@surfaceForm'].replace("'",'') : {'URI': ent['@URI'], 
                'dbpedia_text': (ent['@URI'].split('/')[-1]).replace('_', ' '),
                'proeminence': ent['@support'],
                'dbpedia_types': ent['@types'].split(','),
                'types': [a.split('/')[-1] for a in [q.split(':')[-1] for q in ent['@types'].split(',')]],
                'raw_text': ent['@surfaceForm'].replace("'",''),                
                'pos': int(ent['@offset'])} for ent in result['Resources'] if '@URI' in ent.keys()}     
    return {}


def cogroo_analyze(sentence):
    cogroo = Cogroo.Instance()
    return cogroo.analyze(sentence)


def cogroo_lemmatize(sentence):
    cogroo = Cogroo.Instance()
    return cogroo.lemmatize(sentence)


def get_categorias_dbpedia(resource):
    page = requests.get("http://pt.dbpedia.org/resource/{}".format(resource))
    soup = BeautifulSoup(page.text, 'html.parser')
    a_elements = soup.find_all('a', text=re.compile(".*Categoria.*"))
    
    categorias = set([])
    for elem in a_elements:
        texto = "".join(elem.text.split())
        texto = texto.split("dbr:Categoria:")[1]
        texto = texto.replace("_", " ")
        categorias.add(texto)

    return categorias
    
