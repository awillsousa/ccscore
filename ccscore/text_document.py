from spacy import load
import helper_tools as htools
import split_utils as su
# from tep2 import GrupoSinonimo
from sentence_pair import SentencePair
from single_sentence import SingleSentence
from single_paragraph import SingleParagraph
from paragraph_pair import ParagraphPair
from itertools import combinations
from os import system

class TextDocument(object):
    """
    Class to store a text document
    """
    def __init__(self, text, doc_palavras=None, corref_chains=None):
        """
        :param text: Text of the document.
        """
        self.text = text
        self.doc_palavras = doc_palavras
        self.nlp_processor = None
        self.is_initilized = False
        self.anotated_doc = None
        self.sentences = []
        self.paragraphs = []
        self.local_cohesion_values = []
        self.global_cohesion_values = []    
        self.global_cohesion = None
        self.local_cohesion = None
        self.index_cohesion = None
        self.total_ambiguities = None
        self.total_contradictions = None
        self.index_imprecision = None
        self.total_textual_problems = None
        self.index_form = None

        if corref_chains is None:
            self.corref_chains = {}
        else:
            self.corref_chains = corref_chains

        #requirements_ok, msg = htools.check_requirements()
        requirements_ok = True
        if not requirements_ok:
            print(msg)
            system.exit(99)

        self.__init_document()

    def __init_document(self):
        try:
            if not self.is_initilized:
                if self.nlp_processor is None:
                    self.set_nlp_processor()
                # self.anotated_doc = self.nlp_processor(self.text)
                self.sentences = self.__set_sentences()
                self.paragraphs = self.__set_paragraphs()
                self.is_processed = True
                self.__calc_local_cohesion()
                self.__calc_global_cohesion()
                self.__calc_index_cohesion()
        except Exception as ex:
            print("Error to initialize document.")
            print("Error: ", str(ex))
            self.is_initilized = False

    def set_nlp_processor(self):
        model = load('pt_core_news_lg')
        self.nlp_processor = model

    def __set_paragraphs(self):
        """
        Set the paragraphs that compose the text document
        and the sentences that belong to each paragraph
        """
        paragraphs = []
        paragraphs_texts = [p for p in su.split_by_break(self.text) if len(p) > 0]
        last_pos_sent = 0
        for p_id, p_text in enumerate(paragraphs_texts):
            sentences_id = []
            num_sentences = len(su.split_by_sentence(p_text))

            # BUG do split, quando se passa apenas uma sentença.
            #if len(p_text) > 0 and\
            #    num_sentences == 0:
            #    num_sentences = 1

            for pos_sentence in range(num_sentences):
                sentences_id.append(last_pos_sent)
                last_pos_sent += 1

            paragraphs.append(SingleParagraph(num=p_id,
                                              paragraph_text=p_text,
                                              sentences_id=sentences_id,
                                              doc=self)
                              )

        return paragraphs

    def __set_sentences(self):
        """
        Set the sentences that compose the text document
        """
        sentences = su.split_by_sentence(self.text)
        if self.doc_palavras:
            return [SingleSentence(num=i, sentence_text=s,
                                   annotated_sentence=self.nlp_processor(s),
                                   doc=self, palavras_sentence=self.doc_palavras[i])
                    for i, s in enumerate(sentences)]
        else:
            return [SingleSentence(i, s, self.nlp_processor(s), self)
                    for i, s in enumerate(sentences)]

    def __get_corref_chains(self):
        """
        Get the correference chains of text
        """

        # This way of load the corref chains must be 
        # change in the future
        pass

        

    def __str__(self):
        return self.text

    def __repr__(self):
        repr_str = str(self)
        return repr_str

    def __calc_local_cohesion(self):
        """
        Calculate the local cohesion value
        """
        local_cohesion_values = []
        for s1, s2 in htools.pairwise(self.sentences):
            pair = SentencePair(s1, s2)
            local_cohesion_values.append(pair.calc_local_cohesion())
        self.local_cohesion_values = local_cohesion_values
        self.local_cohesion = sum(local_cohesion_values)

        # return self.local_cohesion
    
    def __calc_global_cohesion(self):
        """
        Calculate the global cohesion value
        """
        global_cohesion_values = []
        for p1, p2 in combinations(self.paragraphs, 2):
            pair = ParagraphPair(p1, p2)
            global_cohesion_values.append(pair.calc_global_cohesion())

        self.global_cohesion_values = global_cohesion_values
        self.global_cohesion = sum(global_cohesion_values)

        # return self.global_cohesion

    def __calc_index_cohesion(self):
        ic = 0
        ic = self.local_cohesion / (len(self.sentences)-1)
        ic += self.global_cohesion / sum(range(len(self.paragraphs)-1))
        ic /= 2

        self.index_cohesion = ic

    def get_sum_local_cohesion(self):
        return self.local_cohesion

    def get_sum_global_cohesion(self):
        return self.global_cohesion

    def get_index_cohesion(self):
        return self.index_cohesion
