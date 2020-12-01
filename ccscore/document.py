from spacy import Doc


# Document class
class Document(Doc):

    def __init__(self, doc_text):
        self.text = doc_text
        self.nlp_text = None

    # Execute action like POS, tokennization, lemmatization, etc
    def preprocess(self):
        self.text
