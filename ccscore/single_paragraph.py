class SingleParagraph(object):
    """
    Class to store a paragraph
    """
    # __slots__ = ['id', 'text', 'sentences', 'list_fe', 'list_fi', 'doc']

    def __init__(self, num, paragraph_text, doc=None):
        """
        Initialize a sentence from the output of one of the supported parsers. 
        It checks for the tokens themselves, pos tags, lemmas
        and dependency annotations.

        :param parser_output: if None, an empty Sentence object is created.
        """
        self.id = num
        self.text = paragraph_text
        self.sentences_id = []
        self.list_fe = []
        self.list_fi = {}
        self.doc = doc
        self.__create_fe()
        self.__create_fi()

    def __str__(self):
        # return ' '.join(str(t) for t in self.tokens)
        return self.text

    def __repr__(self):
        repr_str = str(self)
        return repr_str

    def __create_fe(self):
        """
        Create the explicit focus list
        """
        pass

    def __create_fi(self):
        """
        Create the implicit focus list
        """
        pass
