
def test_text_document(display=True):
    import helper_palavras as h_pal
    from text_document import TextDocument

    original_textfile = "./ccscore/data/texto_exemplo.txt"
    palavras_textfile = "./ccscore/data/texto_exemplo_anotado.html"

    tp = h_pal.parse_file_toclass(palavras_textfile,
                                  original_textfile)
    orig_text = ""
    try:
        with open(original_textfile, 'r') as f_text:
            orig_text = "\n".join(f_text.readlines())
    except IOError:
        print(f"Erro ao tentar abrir o arquivo {original_textfile}")

    td = TextDocument(orig_text, tp)

    if display:
        for i, sent in enumerate(td.sentences):
            print()
            print("ID: ", str(i))
            print("Texto Original: ", sent.text)
            print()
            print("Lista de Foco Explícito: ", [s for s in sent.list_fe])
            print()
            print("Lista de Foco Implícito: ", [s for s in sent.list_fi.items()])
            print()
            print("Lista Intermediária de FE: ", sent.list_fe_li)
            print()
            print("Lista de Entidades Nomeadas: ", sent.named_entities)
            print()
            print("Lista de Menções DBPedia: ", str(sent.dbpedia_mentions))

            print("-"*100)

    return td

def display_text_original():
    original_textfile = "./ccscore/data/texto_exemplo.txt"

    orig_text = []
    try:
        with open(original_textfile, 'r') as f_text:
            orig_text = f_text.readlines()
    except IOError:
        print(f"Erro ao tentar abrir o arquivo {original_textfile}")

    for s in orig_text:
        print(s.replace('\n', ''))


import sys
#sys.path.append('../ccscore/')
import spacy
import pandas as pd
import pickle
from infernal import feature_extraction as fe
from infernal import datastructures as ds
import confapp as config
import helper_palavras as h_pal 
from text_document import TextDocument

def main():            
    PATH_CORPUS = "./ccscore/data/Corpus_Redacoes.pickle"

    # Carrega a base de redações
    df_redacao = pickle.load(open(PATH_CORPUS, 'rb'))
    valores_coesao = {}
    erros = []
    for i, redacao in df_redacao.iterrows():
        #if i > 100:        
        #   break

        texto_orig = str(redacao['Texto']).replace(u"\u2060","")
        texto_pal = redacao['Palavras']
        nota_compt4 = redacao['Competência 4']
        cadeias_corref = redacao['Cadeias']
        try:
            tp = h_pal.parse_text_toclass(texto_pal, texto_orig)
            td = TextDocument(texto_orig, tp, corref_chains=cadeias_corref)
            valor_nota = round(100*td.get_index_cohesion(), 2)
            print(f"Redação: {i}\nIndex Cohesion: {valor_nota} Nota Competência 4: {nota_compt4}")
            valores_coesao[i] = valor_nota
        except Exception as e:
            erros.append((i, str(e)))
            
    print(f"Erros: {str(erros)} Total: {len(erros)}")
    resultados = {"erros": erros,
                  "valores_coesao": valores_coesao}

    pickle.dump(resultados, open('./ccscore/data/resultados_exp_1_1.pickle', 'wb'))
    
if __name__ == '__main__':
    main()
