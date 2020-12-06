from spacy.tokens.doc import Doc
from spacy import load
from single_sentence import SingleSentence


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
                self.anotated_doc = self.nlp_processor(self.text)    
                self.sentences = self.__set_sentences()
                self.is_processed = True            
        except:
            print("Error to initialize document")
            self.is_initilized = False

    def set_nlp_processor(self):        
        model = load('pt_core_news_lg')        
        self.nlp_processor = model                

    def __set_sentences(self):        
        return [SingleSentence(i, s.text, s) for i,s in enumerate(self.anotated_doc.sents)]

    def __str__(self):
        return self.text
    
    def __repr__(self):
        repr_str = str(self)
        return repr_str
    

