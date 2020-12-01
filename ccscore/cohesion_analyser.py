import spacy
from document import Document

nlp_process = spacy.load("")

# Cohesion analyzer class
class CohesionAnalyzer(object):

    def __init__(self):
        self.funcoes_pipeline = [self.]
        self.results = []

    def analyze(self, doc):
        self.results =  [f(doc) for f in self.funcoes_pipeline]
        
    def analyze_local_cohesion(self, doc):
        pass

    def analyze_global_cohesion(self, doc):
        pass

    

