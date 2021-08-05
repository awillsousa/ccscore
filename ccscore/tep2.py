from itertools import combinations 
from collections import defaultdict 
import pickle
import confapp as config


class GrupoSinonimo():
    '''
    Class of Group of synonyms from TeP2
    '''

    def __init__(self):
        self.data = {}
        self.sinonimos = defaultdict(list)
        self.classes = defaultdict(str)
        self.idx_antonimos = defaultdict(int)

    def add(self, idx, dados_grupo):
        '''
        Add word data into group

        :param idx: word index 
        :param dados_grupo: Word group data
    
        '''
        if dados_grupo:            
            self.data[idx] = dados_grupo
            self.set_sinonimos(idx)
            self.set_classes(idx)
        else:
            print("No data to insert.")

    def get(self, idx):
        '''
        Get data from idx index

        :param idx: Index position

        :return Word data
        '''
        return self.data[idx]

    def set_sinonimos(self, idx):     
        '''
        Set synonyms at idx position

        :param int idx: Position to put data
        '''          
        all_sinoms = self.data[idx][1]

        pares_palavras = combinations(all_sinoms, 2)
        for sinonimo_left, sinonimo_right in pares_palavras:
            self.sinonimos[sinonimo_left].append(sinonimo_right)
            self.sinonimos[sinonimo_right].append(sinonimo_left)

    def get_sinonimos(self, palavra):
        '''
        Get word data

        :param str palavra: Word to search

        :return list List of word's synonyms 
        '''

        return self.sinonimos[palavra]

    def set_classes(self, idx):
        '''
        Set word classes 

        :param int idx: Position to set
        '''
        all_sinoms = self.data[idx][1]
        classe = self.data[idx][0]

        for palavra in all_sinoms:            
            self.classes[palavra] = classe

    def get_classe(self, palavra):
        '''
        Get word class

        :param str palavra: Word to get class

        :return list List of classes 
        '''
        return self.classes[palavra]

    def set_antonimos(self, idx):
        '''
        Set antonym at position

        :param int idx: Position to set
        '''
        idx_antonimo = self.data[idx][2]
        all_sinoms = self.data[idx][1]

        for palavra in all_sinoms:
            self.idx_antonimos[palavra] = idx_antonimo

    def get_antonimos(self, palavra):
        '''
        Get word's antonyms  

        :param str palavra: Word to search

        :return list List of word antonyms or None
        '''
        if palavra in self.idx_antonimos.keys():
            data = self.get(self.idx_antonimos[palavra])        
            return data[1]
        else:
            return None

    def get_by_classe(self, classe):
        '''
        Get a list of words from a specific class

        :param str classe: Word class to search

        :return list List of words that belongs to classe
        '''
        return [k for k, v in self.classes.items() if v == classe]
