import spacy
from infernal import feature_extraction as fe

try:
    nlp_process = spacy.load("pt_core_news_lg")
except:
    print("Erro ao carregar modelo spacy")


# Cohesion analyzer class
class CohesionAnalyzer(object):

    def __init__(self, doc):
        self.funcoes_pipeline = [self.anotate_pos,
                                    ]
        self.results = []

        self.textdoc = doc
        self.nlpdoc = None


    def anotate_pos(self):
        self.nlpdoc = nlp_process(self.textdoc)

    def analyze(self):
        self.results =  [f(self.textdoc) for f in self.funcoes_pipeline]
        
    def analyze_local_cohesion(self):
        pass

    def analyze_global_cohesion(self):
        pass

    

