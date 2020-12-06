import spacy
from infernal import feature_extraction as fe

try:
    nlp_process = spacy.load("pt_core_news_lg")
except:
    print("Erro ao carregar modelo spacy")


# 
class CohesionAnalyzer(object):
    """
    Class execute cohesion analyzer
    """

    def __init__(self, doc):
        self.funcoes_pipeline = [self.preprocess_nlp,

                                    ]
        self.results = []

        self.textdoc = doc
        self.nlpdoc = None


    def preprocess_nlp(self):
        proc_doc = anotate_pos(self.textdoc)        

        # Ajusta segmentação de asspas duplas


    def anotate_pos(self, doc):
        return nlp_process(self.textdoc)            


    def analyze(self):
        self.results =  [ f(self.textdoc) for f in self.funcoes_pipeline ]


    def analyze_local_cohesion(self):
        pass


    def analyze_global_cohesion(self):
        pass

    
    def preprocess_pairs(pairs):
        """
        Preprocess the pairs in-place so we can extract features later on.

        :param pairs: list of `SentencePair` objects
        """
        parser_path = config.get_depparse()
        pos_path = config.get_posparse()

        # use spacy's nlp pipeline to run our custom tokenizer and their NER
        nlp_pipeline = spacy.load('pt', disable=['parser', 'tagger'])
        ner = nlp_pipeline.entity

        for i, pair in enumerate(pairs):
            tokens_t = tokenizer.tokenize(pair.t)
            tokens_h = tokenizer.tokenize(pair.h)

            output_t = external.call_corenlp(' '.join(tokens_t), parser_path,
                                            pos_path)
            output_h = external.call_corenlp(' '.join(tokens_h), parser_path,
                                            pos_path)

            # output_t = external.call_corenlp(pair.annotated_t)
            # output_h = external.call_corenlp(pair.annotated_h)

            try:
                pair.annotated_t = ds.Sentence(output_t)
                pair.annotated_h = ds.Sentence(output_h)
            except ValueError as e:
                tb = traceback.format_exc()
                logging.error('Error reading parser output:', e)
                logging.error(tb)
                raise

            # find the named entities and give them to the sentence object
            doc_t = Doc(nlp_pipeline.vocab, words=tokens_t)
            doc_h = Doc(nlp_pipeline.vocab, words=tokens_h)
            ner(doc_t)
            ner(doc_h)
            pair.annotated_t.set_named_entities(doc_t)
            pair.annotated_h.set_named_entities(doc_h)

            pair.find_lexical_alignments()
            pair.find_entity_alignments()

        return pairs
    
