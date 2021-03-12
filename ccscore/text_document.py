from single_paragraph import SingleParagraph
from spacy.tokens.doc import Doc
from spacy import load
import helper_tools as htools
import split_utils as su
import confapp as config
from sentence_pair import SentencePair
from single_sentence import SingleSentence
from tep2 import GrupoSinonimo


class TextDocument(object):
    """
    Class to store a text document
    """
    def __init__(self, text, doc_palavras=None):
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
            paragraph = SingleParagraph(p_id, p_text, self)
            for pos_sentence in range(len(su.split_by_sentence(p_text))):
                paragraph.sentences_id.append(last_pos_sent)
                last_pos_sent += 1
            paragraphs.append(paragraph)

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

    def __str__(self):
        return self.text

    def __repr__(self):
        repr_str = str(self)
        return repr_str

    def calc_local_cohesion(self):
        """
        Calculate the local cohesion value
        """
        local_cohesion_values = []
        for s1, s2 in htools.pairwise(self.sentences):
            pair = SentencePair(s1, s2)
            local_cohesion_values.append(pair.calc_local_cohesion())

        self.local_cohesion = sum(local_cohesion_values)

        return self.local_cohesion
