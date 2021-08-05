import numpy as np
from matplotlib import pyplot as plt
from itertools import combinations
from itertools import tee
from itertools import product
from itertools import zip_longest
from datetime import date


def plot_coesao_local(td, save=False):
    '''
    Plot local cohesion values for one TextDocument instance analyzed.

    The plot show all sentence pairs relations
    
    :param TextDocument td: TextDocument instance
    :param bool save: Store plot into file. Optional (default=False)
    '''

    fig, ax = plt.subplots()    
    y = td.local_cohesion_values
    x = [a+1 for a in list(range(len(td.local_cohesion_values)))]
    plt.ylim(0.0, 1.1)
    plt.yticks(np.arange(0, 1.5, 0.5))
    plt.xticks(np.arange(0, len(x)+1, 1.0))
    plt.xlabel("Pares de Sentenças")
    plt.ylabel("Valores Coesão Local")
    plt.plot(x, y, 'go-')

    a,b = tee(list(range(len(td.sentences))))
    next(b)
    pares_sentencas = list(zip(a,b))
    for i, p in enumerate(list(zip(x,y))):
        px, py = p

        x_text = 13        
        if i % 2 == 0:
            x_text = -1*x_text

        # Anotação dos pares de sentenças    
        ax.annotate(f"{pares_sentencas[i]}", xy=(px,py),
                    textcoords="offset points", 
                     xytext=(x_text,10),
                     ha='center')

    # Caixa com informações adicionais
    text_parag = "\n".join([f"Parágrafo {p.id} : Sentenças ({str(p.sentences_id)})" for p in td.paragraphs])
    #text_valores = "\n".join([f"Coesão Local: {td.local_cohesion}",
    #                          f"Coesão Global: {td.global_cohesion}"])
    text_valores = "\n".join([f"Índice de Coesão: {round(100*td.index_cohesion,2)}"])

    textstr = '\n'.join((r'Num. de Sentenças: %d' % (len(td.sentences),),
                         r'Num. de Parágrafos: %d' % (len(td.paragraphs),),
                         "\n"+text_parag,
                         "\n"+text_valores))    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.1)    
    ax.text(1.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    # Linhas verticais de separação dos parágrafos
    xcoords = [s+1 for p in td.paragraphs for i,s in enumerate(p.sentences_id) if i == (len(p.sentences_id)-1)]    
    xcoords = xcoords[:-1]
    for xc in xcoords:
        plt.axvline(x=xc, color='red', ls=':', lw=2)

    plt.show()
    if save:
        today = date.today()        
        plt.savefig(f"./ccscore/data/coesao_local_{today.strftime('%d_%m_%Y')}.png")

def plot_coesao_global(td, save=False): 
    '''
    Plot global cohesion values for one TextDocument instance analyzed

    The plot show all paragraphs pairs relations

    :param TextDocument td: TextDocument instance
    :param bool save: Store plot into file. Optional (default=False)
    '''
    fig, ax = plt.subplots()    
    y = td.global_cohesion_values
    x = [a+1 for a in list(range(len(td.global_cohesion_values)))]
    plt.ylim(0.0, 1.1)
    plt.yticks(np.arange(0, 1.5, 0.5))
    plt.xticks(np.arange(0, len(td.global_cohesion_values)+1, 1.0))
    plt.xlabel("Pares de Parágrafos")
    plt.ylabel("Valores Coesão Global")
    plt.plot(x, y, 'go-')

    pares_paragraphs = list(combinations(list(range(len(td.paragraphs))),2))
    for i, p in enumerate(list(zip(x,y))):
        px, py = p
        ax.annotate(f"{pares_paragraphs[i]}", xy=(px,py),
                    textcoords="offset points", 
                     xytext=(3,-15),
                     ha='center')

    # Caixa com informações adicionais    
    text_valores = "\n".join([f"Índice de Coesão: {round(100*td.index_cohesion,2)}"])

    textstr = '\n'.join((r'Num. de Parágrafos: %d' % (len(td.paragraphs),),                         
                         "\n"+text_valores))    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.1)    
    ax.text(1.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    # Linhas verticais de separação dos parágrafos
    l_interv = list(range(len(td.paragraphs)-1,0,-1))
    ids_p = [p.id for p in td.paragraphs]
    l_div = [sum(l_interv[0:x:1]) for x in range(0,len(l_interv))]
    xcoords = l_div[1:]    
    
    for xc in xcoords:
        plt.axvline(x=xc, color='blue', ls='--', lw=2)

    plt.show()
    if save:
        today = date.today()        
        plt.savefig(f"./ccscore/data/coesao_local_{today.strftime('%d_%m_%Y')}.png")

def get_ppair_values(td):
    '''
    Get paragraph pairs to help the ploting

    :param TextDocument td: TextDocument instance

    :return list List of paragraphs pairs
    '''
    l_id_p = [a for a in list(range(len(td.paragraphs)))]
    l_prods = [(a,b) for a,b in list(product(l_id_p,l_id_p)) if a != b]    
    l_combs = list(combinations(l_id_p, 2))    
    l_values = td.global_cohesion_values
    x = [a+1 for a in list(range(len(td.global_cohesion_values)))]
    l_valores = list(zip(x,y))

    l_combs_values = []
    l_prod_values = []
    for i_pos, i_prod in enumerate(l_prods):
        if i_prod in l_combs:
            l_pos = l_combs.index(i_prod)
        else:
            a,b = i_prod
            l_pos = l_combs.index((b,a))

        l_prod_values.append((i_pos+1,l_values[l_pos]))

    return l_prods,l_prod_values

def grouper(n, iterable, padvalue=None):
    '''
    Help to create groups of instances (maybe paragraphs or sentences) and fill the
    empty slots in last group if exists any

    :param iter iterable: Iterable to create groups
    :param padvalue: Value to pad in last group, if necessary

    :return Iterable of a list of tuples with groups
    Example: "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    '''
    
    return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

def plot_coesao_global_detail(td, save=False): 
    '''
    Plot global cohesion - detailed version

    :param TextDocument td: TextDocument instance to plot
    :save bool save: Store in file. Optional (default=False)
    '''

    l_prods, l_prod_values = get_ppair_values(td)

    fig, ax = plt.subplots()        
    l_x, l_y = list(zip(*l_prod_values))
    l_x = list(grouper(len(td.paragraphs)-1,l_x))
    l_y = list(grouper(len(td.paragraphs)-1,l_y))    
    l_notes = list(grouper(len(td.paragraphs)-1,l_prods))

    plt.ylim(0.0, 1.1)
    plt.yticks(np.arange(0, 1.5, 0.5))
    plt.xticks(np.arange(0, len(l_prods)+1, 1.0))
    plt.xlabel("Pares de Parágrafos")
    plt.ylabel("Valores Coesão Global")

    xcoords = []
    for x,y,notes in zip(l_x, l_y, l_notes):        
        plt.plot(x, y, 'go-')           

        for i, p in enumerate(list(zip(x,y))):
            px, py = p
            ax.annotate(f"{notes[i]}", xy=(px,py),
                        textcoords="offset points", 
                         xytext=(3,-15),
                         ha='center')
        xcoords.append(x[-1]+0.5)

    for xc in xcoords[:-1]:
        plt.axvline(x=xc, color='blue', ls='--', lw=2)    

    # Caixa com informações adicionais    
    text_valores = "\n".join([f"Índice de Coesão: {round(100*td.index_cohesion,2)}"])

    textstr = '\n'.join((r'Num. de Parágrafos: %d' % (len(td.paragraphs),),                         
                         "\n"+text_valores))    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.1)    
    ax.text(1.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    plt.show()
    if save:
        today = date.today()        
        plt.savefig(f"./ccscore/data/coesao_local_{today.strftime('%d_%m_%Y')}.png")