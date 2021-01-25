import requests
import confapp as config

# Endpoint DBPedia
URL_REST_DBPEDIA = "http://{}:{}/rest/annotate".format(config.DBPEDIA_IP, config.DBPEDIA_PORT)


def get_dbpedia_entries(text, url=URL_REST_DBPEDIA):
    """
    Get entities mentions by calling a DBpedia Spotlight REST API

    :param text: Text to be analyzed
    :param url: endpoint to annotate text
    """
    
    # params to rest call 
    PARAMS = {'confidence':0.35, 'text': text, 'policy': 'blacklist'} 
    #PARAMS = {'confidence':0.35, 'text': texto, 'policy': 'whitelist'} 
    
    # send request 
    r = requests.get(url = url, params = PARAMS, headers={'Accept': "application/json"}) 
    
    # Get result in json format 
    result = r.json() 
  
    return format_dbpedia_result(result)


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