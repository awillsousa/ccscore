texto = '''Defendida por agentes do mercado financeiro e uma das bandeiras da equipe econômica do governo Jair Bolsonaro, o projeto de autonomia do Banco Central (BC) deve avançar na Câmara só após a reforma tributária andar, no que depender do presidente da Casa, Rodrigo Maia (DEM-RJ). Para ele, o projeto sobre a instituição presidida por Roberto Campos Neto não é urgente no curto prazo.

Aceito votar autonomia do Banco, aceito, é claro, votar os depósitos voluntários, mas aí temos que organizar melhor a pauta até o fim do ano. É só o governo ter boa vontade na reforma tributária", disse Maia, ao participar de evento organizado pelo Itaú. "A reforma tributária tem importância muito maior que autonomia do Banco Central", comentou.

O projeto de autonomia do BC foi aprovado na terça-feira, 3, pelo Senado e agora precisa do aval dos deputados para virar lei. O texto mantém o controle dos preços como objetivo central, mas inclui ainda duas novas metas acessórias, sem prejuízo à principal: suavizar as flutuações do nível de atividade econômica e fomentar o pleno emprego no País. O governo concordou com a redação da proposta, apesar de o BC ser historicamente contrário a ampliar o escopo da atuação.

Maia já reclamou outras vezes da falta de empenho e atuação do governo para se aprovar a medida. Na semana passada, acusou o presidente do Banco Central, Roberto Campos Neto, de ter vazado informações sobre conversa que os dois tiveram no dia da decisão do Comitê de Política Monetária (Copom), que manteve a taxa Selic em 2% ao ano.

Ao jornal O Estado de S. Paulo, Maia criticou a articulação do presidente do BC em alertar sobre os reflexos para a economia da dificuldade do Congresso em avançar com as votações da pauta de ajuste fiscal. Segundo o presidente da Câmara, Campos Neto tentou fazer uma articulação política, sem combinar, o que não seria papel dele, mas dos ministros da Economia, Paulo Guedes, e da articulação política, Luiz Eduardo Ramos.

Nesta sexta-feira, o presidente da Câmara lembrou que havia uma proposta de autonomia do BC semelhante na Câmara, mas que não foi votada, e disse que não comentou até agora sobre o tema porque não foi procurado pelo governo para falar sobre o assunto. "Se eu conseguisse conversar com alguém do governo, eu poderia te responder, mas ninguém me procura. Não vou conversar com a imprensa antes de conversar com o governo", disse.

Como o Broadcast (sistema de notícias em tempo real do Grupo Estado) mostrou na quinta-feira, deputados já se articulam na Câmara para modificar o projeto aprovado pelo Senado. O partido Novo, por exemplo, quer enxugar a proposta que recebeu aval dos senadores para reduzir os chamados acessórios que foram colocados para o Banco Central.

Sobre a reforma tributária, Maia deu sinais de que quer aprovar o projeto antes de deixar a presidência da Casa e acredita que com acordo pode fazer isso rapidamente.'''


'''
from text_document import TextDocument
td = TextDocument(texto)

for i, sent in enumerate(td.sentences):
    print()
    print("ID: ", str(i))    
    print("Texto Original: ", sent.text)    
    print()    
    print("Lista de Foco Explícito: ", [s for s in sent.list_fe])    
    print()
    print("Lista Intermediária de FE: ", sent.list_fe_li)
    print()    
    print("Lista de Entidades Nomeadas: ", sent.named_entities)    
    print()
    print("Lista de Menções DBPedia: ", str(sent.dbpedia_mentions))    
    
    print("-"*100)
'''

def test_text_document(display=True):
    import helper_palavras as h_pal 
    from text_document import TextDocument

    original_textfile = "./ccscore/data/texto_exemplo.txt"
    palavras_textfile = "./ccscore/data/texto_exemplo_anotado.html"

    tp = h_pal.parse_file_toclass(palavras_textfile,
                                original_textfile)


    try:
        with open(original_textfile, 'r') as f_text:
                orig_text = "\n".join(f_text.readlines())
    except IOError:
        print(f"Erro ao tentar abrir o arquivo {original_text}")

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

def sentence_pair(td):
    from sentence_pair import SentencePair

    s1 = td.sentences[0]
    s2 = td.sentences[1]

    sent_pair = SentencePair(s1, s2)

    print(sent_pair.calc_local_cohesion())

def calculate_local_cohesion(td):
    return td.calc_local_cohesion()

    

def main():
    #sentence_pair(test_text_document(display=False))
    calculate_local_cohesion(test_text_document(display=False))


if __name__ == '__main__':
    main()
