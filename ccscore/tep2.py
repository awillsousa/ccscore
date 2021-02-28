from itertools import combinations 
from collections import defaultdict 
import pickle
import confapp as config


class GrupoSinonimo():

    def __init__(self):
        self.data = {}
        self.sinonimos = defaultdict(list)
        self.classes = defaultdict(str)
        self.idx_antonimos = defaultdict(int)

    def add(self, idx, dados_grupo):
        if dados_grupo:            
            self.data[idx] = dados_grupo
            self.set_sinonimos(idx)
            self.set_classes(idx)
        else:
            print("Sem dados para inserir")

    def get(self, idx):
        return self.data[idx]

    def set_sinonimos(self, idx):               
        all_sinoms = self.data[idx][1]

        pares_palavras = combinations(all_sinoms, 2)
        for sinonimo_left, sinonimo_right in pares_palavras:
            self.sinonimos[sinonimo_left].append(sinonimo_right)
            self.sinonimos[sinonimo_right].append(sinonimo_left)

    def get_sinonimos(self, palavra):
        return self.sinonimos[palavra]

    def set_classes(self, idx):
        all_sinoms = self.data[idx][1]
        classe = self.data[idx][0]

        for palavra in all_sinoms:
            # print("classe: " + classe + " " + "palavra: " + palavra)
            self.classes[palavra] = classe

    def get_classe(self, palavra):
        return self.classes[palavra]

    def set_antonimos(self, idx):
        idx_antonimo = self.data[idx][2]
        all_sinoms = self.data[idx][1]

        for palavra in all_sinoms:
            self.idx_antonimos[palavra] = idx_antonimo

    def get_antonimos(self, palavra):
        if palavra in self.idx_antonimos.keys():
            data = self.get(self.idx_antonimos[palavra])        
            return data[1]
        else:
            return None

    def get_by_classe(self, classe):
        return [k for k, v in self.classes.items() if v == classe]
