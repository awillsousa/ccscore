import helper_palavras as h_pal
from text_document import TextDocument
import pandas as pd
import argparse
import pickle

parser = argparse.ArgumentParser()

def test_text_document(td, tp, display=True):    
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

def paragraph_pair(td, display_sentences=False):
    from paragraph_pair import ParagraphPair
    from itertools import combinations
    recuo = "\t\t"
    for p1, p2 in combinations(td.paragraphs, 2):
        parag_pair = ParagraphPair(p1, p2)
        print()
        print(f"Par: ({p1.id}, {p2.id}) ")
        print()
        print("Texto Original: ")
        print(f"Paragrafo {p1.id}:", p1.text)
        print("Foco Explicito: [", f"\n{recuo}".join([x for x in p1.list_fe]), "]")
        print("Foco Implicito: {", f"\n{recuo}".join([f"{str(x)}:{str(y)}"
                                                  for x, y in p1.list_fi.items()]), "}")
        if display_sentences:            
            print(f"\n{recuo}", "="*40, " SENTENÇAS ", "="*40)
            for s in p1.get_sentences():
                print(f"{recuo}Sentença {s.id}:", s.text)
                print(f"{2*recuo}Foco Explicito: [", f"\n{3*recuo}".join([x for x in s.list_fe]), "]")
                print(f"{2*recuo}Foco Implicito: ", "{",
                                                        f"\n{3*recuo}".join([f"{str(x)}:{str(y)}"
                                                        for x, y in s.list_fi.items()]), 
                                                    "}")
                print()
        print(f"\n{recuo}", "="*40, "  ", "="*40)                
        print()
        print(f"Paragrafo {p2.id}:", p2.text)
        print("Foco Explicito: [", f"\n{recuo}".join([x for x in p2.list_fe]), "]")
        print("Foco Implicito: {", f"\n{recuo}".join([f"{str(x)}:{str(y)}"
                                                  for x, y in p2.list_fi.items()]), "}")
        if display_sentences:
            print(f"\n{recuo}", "="*40, " SENTENÇAS ", "="*40)
            for s in p2.get_sentences():
                print(f"{recuo}Sentença {s.id}:", s.text)
                print(f"{2*recuo}Foco Explicito: [", f"\n{3*recuo}".join([x for x in s.list_fe]), "]")
                print(f"{2*recuo}Foco Implicito: ", "{", 
                                                        f"\n{3*recuo}".join([f"{str(x)}:{str(y)}"
                                                        for x, y in s.list_fi.items()]),
                                                    "}")
                print()
        print(f"\n{recuo}", "="*40, "  ", "="*40)
        print()
        print("Lista de Foco Explícito: ", str(parag_pair.fe_intersection))
        print()
        print("Lista de Foco Implícito: ", str(parag_pair.fi_intersection))
        print()
        print(parag_pair.calc_global_cohesion())
        print("-"*100)


def sentence_pair(td):
    from sentence_pair import SentencePair
    from helper_tools import pairwise

    for s1, s2 in pairwise(td.sentences):
        sent_pair = SentencePair(s1, s2)
        print()
        print("Texto Original: ")
        print("Sentença 1:", s1.text)
        print("Foco Explicito: [", "\n\t\t".join([x for x in s1.list_fe]), "]")
        print("Foco Implicito: {", "\n\t\t".join([f"{str(x)}:{str(y)}"
                                                  for x, y in s1.list_fi.items()]), "}")
        print()
        print("Sentença 2:", s2.text)
        print("Foco Explicito: [", "\n\t\t".join([x for x in s2.list_fe]), "]")
        print("Foco Implicito: {", "\n\t\t".join([f"{str(x)}:{str(y)}"
                                                  for x, y in s2.list_fi.items()]), "}")
        print()
        print("Lista de Foco Explícito: ", str(sent_pair.fe_intersection))
        print()
        print("Lista de Foco Implícito: ", str(sent_pair.fi_intersection))
        print()
        print(sent_pair.calc_local_cohesion())
        print("-"*100)


def calc_local_cohesion(td):
    print(f"Total LOCAL Cohesion: {td.calc_local_cohesion()}")


def calc_global_cohesion(td):
    print(f"Total GLOBAL Cohesion: {td.calc_global_cohesion()}")


def calc_index_cohesion(td):
    print(f"Index Cohesion: {td.get_index_cohesion()}")


def display_text_original():
    original_textfile = "./ccscore/data/texto_exemplo.txt"

    orig_text = []
    try:
        with open(original_textfile, 'r') as f_text:
            orig_text = f_text.readlines()
    except IOError:
        print(f"Erro trying to open file {original_textfile}")

    for s in orig_text:
        print(s.replace('\n', ''))


def main(num_redacao):
    PATH_CORPUS = "./ccscore/data/Corpus_Redacoes.pickle"
    # Carrega a base de redações
    try:
        df_redacao = pickle.load(open(PATH_CORPUS, 'rb'))
        redacao = df_redacao.iloc[num_redacao]
    except IOError:
        print("Error loading file")
    except Exception as e:
        print(f"Erro: {str(e)}")
    finally:
        df_redacao = None

    texto_orig = str(redacao.Texto).replace(u"\u2060", "")
    texto_pal = redacao.Palavras
    cadeias_corref = redacao.Cadeias

    tp = h_pal.parse_text_toclass(texto_pal, texto_orig)
    td = TextDocument(texto_orig, tp, corref_chains=cadeias_corref)

    calc_index_cohesion(test_text_document(td, tp, display=True))


if __name__ == '__main__':
    
    parser.add_argument("--num_redacao", 
                        help="Número da redação a ser exibida",
                        type=int)
    args = parser.parse_args()    
    main(args.num_redacao)
