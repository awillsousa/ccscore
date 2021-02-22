from spacy.tokens.doc import Doc
from spacy import load
import split_utils as su
from single_sentence import SingleSentence
import confapp as config


class TextDocument(object):
    """
    Class to store a text document
    """
    def __init__(self, text):
        """        
        :param text: Text of the document.
        """        
        self.text = text                        
        self.nlp_processor = None
        self.is_initilized = False
        self.anotated_doc = None         
        self.sentences = None
        self.__init_document()

    def __init_document(self):
        try:
            if not self.is_initilized:
                if self.nlp_processor is None:
                    self.set_nlp_processor()
                #self.anotated_doc = self.nlp_processor(self.text)    
                self.sentences = self.__set_sentences()
                self.is_processed = True            
        except Exception as ex:
            print("Error to initialize document.")
            print("Error: ", str(ex))
            self.is_initilized = False

    def set_nlp_processor(self):        
        model = load('pt_core_news_lg')        
        self.nlp_processor = model                

    def __set_sentences(self):        
        sentences = su.split_by_sentence(self.text)
        return [SingleSentence(i, s, self.nlp_processor(s), self) for i,s in enumerate(sentences)]

    def __set_sentences2(self):
        sentences = []
        add_asspas = False
        id_sent = 0
        for i,s in enumerate(self.anotated_doc.sents):
            if s.text == '"':
                add_asspas = True
            else:
                if add_asspas:
                    sentences.append(SingleSentence(id_sent, '"'+s.text, self.nlp_processor('"'+s.text), self.anotated_doc))
                else:
                    sentences.append(SingleSentence(id_sent, s.text, s, self.anotated_doc))
                id_sent += 1

        #return [SingleSentence(i, s.text, s, self.anotated_doc) for i,s in enumerate(self.anotated_doc.sents)]
        return sentences


    def __str__(self):
        return self.text
    
    def __repr__(self):
        repr_str = str(self)
        return repr_str
    

