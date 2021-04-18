#!/usr/bin/env python
# coding: utf-8

# ### Processo de Extração de Entidades e Recuperação de Dados da Wikidata
# Neste notebook serão executadas as ações de recuperação das entidades do corpus de redações e 
# também, a recuperação de dados dessas entidades, a partir da wikidata, para assim gerar
# uma lista de entidades e os seus possíveis alias.

#import pandas as pd
#import wikidata
#from urllib.error import HTTPError
import functools
import json
import helper_dbpedia as dbpedia
import requests
from requests.exceptions import HTTPError
from wikidata.client import Client
import pydash
import itertools
from pymongo import MongoClient
import multiprocessing

GLOBALLOCK = multiprocessing.Lock()

MONGO_IP_SERVER = "willbot"
MONGO_ROOT = "root"
MONGO_PASS = "Ktap1mb@!"
PATH_TODAS_REDACOES = "ccscore/data/all_texts.txt"

def get_wikipedia_page(item_wiki, show_raw=False):    
    URL_REQUEST=f"https://pt.wikipedia.org/w/api.php?action=query&prop=pageprops&format=json&titles={item_wiki}"
    try:
        response = requests.get(URL_REQUEST)    
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'Erro HTTP: {http_err}') 
    except Exception as err:
        print(f'Erro genérico: {err}')

    dados_wiki_item = json.loads(response.content)

    if show_raw:
        print(json.dumps(dados_wiki_item, indent=3))

    wikibase_item = None        
    type_item = 'REDIRECT_PAGE'
    title_item = ""
    is_disambiguation_page = False
    is_redirect_page = True
    query = dados_wiki_item['query'] if 'query' in dados_wiki_item.keys() else None
    pages = query['pages'] if 'pages' in query.keys() else None
    for p in pages.values():
        for k,v in p.items():
            if k == 'pageprops':
                is_redirect_page = False
                if 'wikibase_item' in v.keys():
                    type_item='WIKIBASE_ITEM'
                    wikibase_item = v['wikibase_item']
                if 'disambiguation' in v.keys():
                    type_item='DISAMBIGUATION_PAGE'
                    is_disambiguation_page = True
            elif k == 'title':
                title_item = v
      
    return type_item, wikibase_item, title_item


def get_redirect_page(item_wiki, show_raw=False):
    URL_REQUEST=f"https://pt.wikipedia.org/w/api.php?action=query&&redirects&format=json&titles={item_wiki}"

    try:
        response = requests.get(URL_REQUEST)    
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'Erro HTTP: {http_err}') 
    except Exception as err:
        print(f'Erro genérico: {err}')    

    dados_wiki_item = json.loads(response.content)

    if show_raw:
        print(json.dumps(dados_wiki_item, indent=3))

    #redirect_to = pydash.get(dados_wiki_item, 'query.redirects[0].to')
    redirects = pydash.get(dados_wiki_item, 'query.redirects')

    results = []
    if not(redirects is None):
        #if len(redirects) > 0:
        for r_item in redirects:
            redirect_to = r_item['to']
            results.append(get_wikipedia_page(item_wiki=redirect_to,
                                            show_raw=show_raw))

    return results


def get_disambiguation_page(item_wiki, show_raw=False):
    URL_REQUEST=f"https://pt.wikipedia.org/w/api.php?action=query&generator=links&format=json&redirects=1&prop=pageprops&gpllimit=50&ppprop=wikibase_item&titles={item_wiki}"
    DESCARTE_QIDS = ['Q4167410',   # Wikipedia:Desambiaguação
                     'Q151',           # Wikcionário
                     'Q4167836',       # Wikimedia category                 
                    ]  
    try:
        response = requests.get(URL_REQUEST)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'Erro HTTP: {http_err}')
    except Exception as err:
        print(f'Erro genérico: {err}')

    dados_wiki_item = json.loads(response.content)

    if show_raw:
        print(json.dumps(dados_wiki_item, indent=3))

    redirects = []

    redirects_from = pydash.get(dados_wiki_item, 'query.redirects.from')
    if not(redirects_from is None):
        redirects += redirects_from

    redirects_to = pydash.get(dados_wiki_item, 'query.redirects.to')
    if not(redirects_to is None):
        redirects += redirects_to

    redirects = set(redirects)
    pages = pydash.get(dados_wiki_item, 'query.pages')

    if show_raw:
        print(f"\n{50*'='}\n")
        print(json.dumps(pages, indent=3))
        print(f"\n{50*'='}\n")

    results = []
    if not(pages is None):
        for p_item in pages.values():
            p_item_title = p_item['title']
            p_wikibase_item = pydash.get(p_item, "pageprops.wikibase_item")

            # não quero redirects
            if p_item_title in redirects:
                continue

            # não quero itens vazios e itens da lista
            # de descarte
            if p_wikibase_item is None or \
               p_wikibase_item in DESCARTE_QIDS:
                continue

            # Recupera a pagina referente ao item
            tipo, item, title = get_wikipedia_page(p_item_title, show_raw)

            # Queremos apenas itens da wikidata, sem páginas
            # de redirecionamento e desambiguação
            if tipo == 'WIKIBASE_ITEM':
                results.append((tipo, item, title))

    return results


def get_wikipedia_data(item_wiki, show_raw=False):
    tipo, item, title = get_wikipedia_page(item_wiki, show_raw)

    result = []

    if tipo == 'WIKIBASE_ITEM':
        print("O item consultado é um 'item direto da wikipedia'.")        
        result = [ (tipo, item, title) ]
    elif tipo == 'REDIRECT_PAGE':    
        print("O item consultado é uma página de redirecionamento.")
        result_redir = get_redirect_page(item_wiki, show_raw)

        # As vezes a pagina de redirecionamento pode levar
        # para uma pagina de desambiguacao
        if len(result_redir) == 1 and \
           result_redir[0][0] == 'DISAMBIGUATION_PAGE':
            result = get_disambiguation_page(item_wiki, show_raw)
        else:
            result = result_redir
    elif tipo == 'DISAMBIGUATION_PAGE':    
        print("O item consultado é uma página de desambiguação.")        
        result = get_disambiguation_page(item_wiki, show_raw)

    return result


def get_str_lang(item):
    STR_PTBR = 'pt-br'
    STR_PT = 'pt'
    STR_EN = 'en'
    if isinstance(item, dict):
        if STR_PTBR in item.keys():
            return STR_PTBR
        elif STR_PT in item.keys():
            return STR_PT
        elif STR_EN in item.keys():
            return STR_EN
        else:
            return None


def get_field_values(wikidata_item, item_field):
    str_lang = get_str_lang(wikidata_item.data[item_field])
    values_field = []
    if str_lang:
        if isinstance(wikidata_item.data[item_field][str_lang], dict):
            values_field = [
                             elem for k, elem in wikidata_item.data[item_field][str_lang].items() 
                                  if k == 'value'
                           ]
        elif isinstance(wikidata_item.data[item_field][str_lang], list):
            values_field = [
                             elem for x in wikidata_item.data[item_field][str_lang] 
                                      for k,elem in x.items() if k == 'value'
                           ]    

    return values_field


def get_wikidata_aliases(wikibase_item):

    aliases_pt_all = []

    aliases_ptbr = pydash.get(wikibase_item.data, 'aliases.pt-br')        
    if not(aliases_ptbr is None):
        aliases_pt_all += list({ x['value'] for x in aliases_ptbr })

    aliases_pt = pydash.get(wikibase_item.data, 'aliases.pt')        
    if not(aliases_pt is None):
        aliases_pt_all += list({ 
                                x['value'] for x in aliases_pt 
                                    if not(x['value'] in aliases_pt_all)
                               })

    return list(aliases_pt_all)


def get_wikidata_descriptions(wikibase_item):

    desc_pt_all = set([])

    desc_ptbr = pydash.get(wikibase_item.data, 'descriptions.pt-br.value')
    if not(desc_ptbr is None):
        desc_pt_all.add(desc_ptbr)

    desc_pt = pydash.get(wikibase_item.data, 'descriptions.pt.value')
    if not(desc_pt is None):
        desc_pt_all.add(desc_pt)

    return list(desc_pt_all)


def get_wikidata_labels(wikibase_item):
    labels_pt_all = set([])

    labels_ptbr = pydash.get(wikibase_item.data, 'labels.pt-br.value')        
    if not(labels_ptbr is None):
        labels_pt_all.add(labels_ptbr) 

    labels_pt = pydash.get(wikibase_item.data, 'labels.pt.value')    
    if not(labels_pt is None):
        labels_pt_all.add(labels_pt)

    return list(labels_pt_all)


def get_wikidata_info(wikibase_item):

    client_wikidata = Client()
    try:
        wikidata_item = client_wikidata.get(wikibase_item, load=True)

        labels_item = get_wikidata_labels(wikidata_item)
        descriptions_item = get_wikidata_descriptions(wikidata_item)    
        aliases_item = get_wikidata_aliases(wikidata_item)    

        return labels_item, descriptions_item, aliases_item

    except HTTPError as e:
        if e.code == 404:
            print(f"Item não encontrado na WikiData - erro {e.code}")
        else:
            print(f"Erro HTTP \n Erro {e.code}")


def get_wikientity_data(item_query, show_raw=False):
    wikipedia_data = get_wikipedia_data(item_query, show_raw)
    items = []
    for tipo, item_id, title in wikipedia_data:
        labels_item, descriptions_item, aliases_item = get_wikidata_info(item_id)        
        item_data = {'id': item_id,
                     'title': title,
                     'labels': labels_item,
                     'descriptions': " ".join(descriptions_item),
                     'aliases': aliases_item}
        items.append(item_data)

        if show_raw:
            print(f"\nItem consultado: {title} - {item_id}\n")
            print(item_data,"\n")
    return items


def get_line():
    with open(PATH_TODAS_REDACOES, 'r') as arq_redacoes:
        for linha in arq_redacoes:
            yield linha


def e_linha_titulo(linha):
    return "<ARQUIVO: " in linha or \
           linha == ""


def get_redacao():
    with open(PATH_TODAS_REDACOES, 'r') as arq_redacoes:        
        for key, group in itertools.groupby(arq_redacoes, e_linha_titulo):            
            if not key:
                yield "".join(list(group))


def get_mongo_client():
    try:
        mongoclient = MongoClient(MONGO_IP_SERVER, 
                                  username=MONGO_ROOT, 
                                  password=MONGO_PASS)

        return mongoclient
    except Exception as e:
        print(str(e))
        return None


def get_mongo_db(database, mongo_client=None):
    if mongo_client is None:
        mongo_client = get_mongo_client()

    return mongo_client[database]


def get_mongo_collection(collection_name, mongo_db):
    dic_collection = None
    try:
        if collection_name not in mongo_db.list_collection_names():
            dic_collection = mongo_db.create_collection(collection_name)
        else:
            dic_collection = mongo_db[collection_name]
    except Exception as e:
        print(f"Erro ao tentar criar a collection {collection_name}")
        print(str(e))

    return dic_collection


def insere_entidade_db(collection, entity_obj):  
    '''
    Insere um objeto entidade no MongoDB
    Esperar um objeto do tipo:
    r_jsonl = {'id': id_item,
                   'name': titulo,
                   'description': descricao,
                   'label': ""
                    }
    '''
    qtd_ents = collection.count_documents({'name': entity_obj['name']})

    if qtd_ents == 0:    
        try:
            id_inserted = collection.insert_one(entity_obj).inserted_id

            return id_inserted
        except Exception as e:
            print(f"Erro ao tentar inserir a entidade {entity_obj['name']}")
            print(str(e))
    else:
        return None


def get_entity_by_qid(collection, id_entity):    
    q_entity = collection.find_one({'id': id_entity})

    return q_entity


def reajusta_probs(num_items):
    '''
    Ajusta os valores de probabilidade, distribuindo
    os valores de acordo com a quantidade de itens
    '''
    l_r = num_items*[round(1/num_items, 2)]

    if sum(l_r) < 1.0:
        l_r[0] += (1 - sum(l_r))
    elif sum(l_r) > 1.0:
        l_r[-1] -= (sum(l_r)-1)

    return l_r


def insere_alias_db(collection, alias_obj):
    '''
    Insere um objeto alias no MongoDB
    Esperar um objeto do tipo:
    a_jsonl = {'alias': titulo,
                   'entities': [id_item],
                   'probabilities': [1.0]}
    '''
    # Verifica se o alias inserido já existe
    qtd_alias = collection.count_documents({'alias': alias_obj['alias']})

    if qtd_alias == 0:  # não existe no db                
        try:
            id_inserted = collection.insert_one(alias_obj).inserted_id

            return id_inserted
        except Exception as e:
            print(f"Erro ao tentar inserir aliases na base. \n{str(e)}")
            return None
    else:   # substitui
        doc_alias = collection.find_one({'alias': alias_obj['alias']})
        qt_entities = len(doc_alias['entities'])
        new_entity_list = list(set(doc_alias['entities']+alias_obj['entities']))
        new_qt_entity_list = len(new_entity_list)
        if qt_entities < new_qt_entity_list: # alguma entitidade foi acrescida?
            new_probs = reajusta_probs(new_qt_entity_list)
            result = collection.update_one(
                            {"_id" : doc_alias["_id"]},
                            {
                                "$set": {'entities': new_entity_list,
                                    'probabilities': new_probs}
                            },
                            upsert=True)
            if not result.acknowledged:
                print(f"Erro ao tentar atualizar o documento {doc_alias['_id']}")
        else:  # não há nada de novo para acrescentar
            return None


def get_alias_by_name(collection, name_alias):
    mongo_alias = collection.find_one({'alias': name_alias})

    if not (mongo_alias is None):
        return mongo_alias
    else:
        return None


def worker_processa_redacao(redacoes):
    ####################
    GLOBALLOCK.acquire()
    ####################

    kb_mongo = get_mongo_db("kb")
    raw_kb = get_mongo_collection("raw_kb", kb_mongo)
    entidades_kb = get_mongo_collection("entidades_kb", kb_mongo)
    alias_kb = get_mongo_collection("alias_kb", kb_mongo)

    ####################
    GLOBALLOCK.release()
    ####################

    for num_redacao, redacao in enumerate(redacoes):
        if len(redacao) < 5:
            continue

        #print()
        #print(50*"=")
        #print(f"Processando redação {num_redacao}")
        #print(50*"=")        
        entidades_dbpedia = dbpedia.get_dbpedia_entries(redacao)

        for t_ent, d_ent in entidades_dbpedia.items():
            try:
                print(f"Processando entidade {t_ent}")

                #qtd_ents = raw_kb.count_documents({'dbpedia_text': d_ent['dbpedia_text']})
                qtd_ents = raw_kb.count_documents({'dbpedia_text': d_ent['raw_text']})

                if qtd_ents > 0: # inserir apenas um documento por item
                    print(f"Entidade {t_ent} já existe na base de dados.\n")
                else:                 
                    id_inserido = raw_kb.insert_one(d_ent).inserted_id
                    print(f"Inserido id {id_inserido}")

                    #wikidata_items = get_wikientity_data(d_ent['dbpedia_text'])
                    wikidata_items = get_wikientity_data(d_ent['raw_text']) 
                    for item_data in wikidata_items:
                        #print(f"\n\nitem_data {item_data}\n\n")
                        item_data_id   = item_data['id']
                        item_data_name = item_data['title']
                        item_data_desc = item_data['descriptions']
                        item_data_labels = item_data['labels']
                        item_data_aliases = item_data['aliases']

                        ####################
                        GLOBALLOCK.acquire()
                        ####################

                        # Insere entidade
                        r_jsonl = {
                                    'id': item_data_id,
                                    'name': item_data_name,
                                    'description': item_data_desc,
                                    'label': "",  # este campo é um indicador da base de conhecimento 
                                                    # diferente do label retornado da wikidata
                                  }
                        insere_entidade_db(entidades_kb, r_jsonl)

                        # Insere um alias equivalente a entidade
                        a_jsonl = {
                                    'alias': item_data_name,
                                    'entities': [item_data_id],
                                    'probabilities': [1.0]
                                  }
                        insere_alias_db(alias_kb, a_jsonl)

                        # Se o titulo for diferente dos labels da wikidata
                        # insere um alias equivalente
                        for alias_l in [l for l in item_data_labels if item_data_name.lower() != l.lower()]:
                            a_jsonl = {
                                        'alias': alias_l,
                                        'entities': [item_data_id],
                                        'probabilities': [1.0]
                                      }
                            insere_alias_db(alias_kb, a_jsonl)

                        # Insere os alias
                        for alias_l in item_data_aliases:
                            a_jsonl = {
                                        'alias': alias_l,
                                        'entities': [item_data_id],
                                        'probabilities': [1.0]
                                      }            
                            insere_alias_db(alias_kb, a_jsonl)
                    
                        ####################
                        GLOBALLOCK.release()
                        ####################
            except Exception as e:
                print(f"Erro processando entidade {t_ent}")
                print(f"Erro: {str(e)}")


def processa_redacoes(redacoes):
    
    kb_mongo = get_mongo_db("kb")
    raw_kb = get_mongo_collection("raw_kb", kb_mongo)
    entidades_kb = get_mongo_collection("entidades_kb", kb_mongo)
    alias_kb = get_mongo_collection("alias_kb", kb_mongo)
    
    for num_redacao, redacao in enumerate(redacoes):
        if len(redacao) < 5:
            continue

        #print()
        #print(50*"=")
        #print(f"Processando redação {num_redacao}")
        #print(50*"=")        
        entidades_dbpedia = dbpedia.get_dbpedia_entries(redacao)

        for t_ent, d_ent in entidades_dbpedia.items():
            try:
                print(f"Processando entidade {t_ent}")
                
                #qtd_ents = raw_kb.count_documents({'dbpedia_text': d_ent['dbpedia_text']})
                qtd_ents = raw_kb.count_documents({'dbpedia_text': d_ent['raw_text']})
                
                if qtd_ents > 0: # inserir apenas um documento por item
                    print(f"Entidade {t_ent} já existe na base de dados.")
                else:                 
                    id_inserido = raw_kb.insert_one(d_ent).inserted_id
                    print(f"Inserido id {id_inserido}")
                
                    #wikidata_items = get_wikientity_data(d_ent['dbpedia_text'])
                    wikidata_items = get_wikientity_data(d_ent['raw_text']) 
                    for item_data in wikidata_items:
                        #print(f"\n\nitem_data {item_data}\n\n")
                        item_data_id   = item_data['id']
                        item_data_name = item_data['title']
                        item_data_desc = item_data['descriptions']
                        item_data_labels = item_data['labels']
                        item_data_aliases = item_data['aliases']

                        # Insere entidade 
                        r_jsonl = {
                                'id': item_data_id,
                                'name': item_data_name,
                                'description': item_data_desc,
                                'label': "",  # este campo é um indicador da base de conhecimento 
                                                # diferente do label retornado da wikidata
                                }
                        insere_entidade_db(entidades_kb, r_jsonl)

                        # Insere um alias equivalente a entidade
                        a_jsonl = {
                                'alias': item_data_name,
                                'entities': [item_data_id],
                                'probabilities': [1.0]
                                }
                        insere_alias_db(alias_kb, a_jsonl)

                        # Se o titulo for diferente dos labels da wikidata
                        # insere um alias equivalente
                        for alias_l in [l for l in item_data_labels if item_data_name.lower() != l.lower()]:
                            a_jsonl = {
                                    'alias': alias_l,
                                    'entities': [item_data_id],
                                    'probabilities': [1.0]
                                    }
                            insere_alias_db(alias_kb, a_jsonl)

                        # Insere os alias
                        for alias_l in item_data_aliases:
                            a_jsonl = {
                                    'alias': alias_l,
                                    'entities': [item_data_id],
                                    'probabilities': [1.0]
                                    }            
                            insere_alias_db(alias_kb, a_jsonl)

            except Exception as e:
                print(f"Erro processando entidade {t_ent}")
                print(f"Erro: {str(e)}")

def main():

    #df_redacoes = pd.read_json("ccscore/data/todas_redacoes_norm.json")
    
    i = 0 
    redacoes = []
    for r in get_redacao():        
        redacoes.append(r)    
    
    print(f"Processando {len(redacoes)} redações ...")

    multiproc = True
    if multiproc:

        num_procs = 20
        n = len(redacoes)//num_procs
        chunks_redacoes = [redacoes[i * n:(i + 1) * n] for i in range((len(redacoes) + n - 1) // n )]
        p = multiprocessing.Pool(num_procs)
        r_multiproc = p.map( worker_processa_redacao, chunks_redacoes)
        p.close()
        p.join()
        #print(r_multiproc)

    else:
        processa_redacoes(redacoes)

if __name__ == "__main__":
    main()