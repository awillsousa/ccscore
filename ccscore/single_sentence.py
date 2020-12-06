
from dependency import Dependency


class SingleSentence(object):
    """
    Class to store a sentence with linguistic annotations.
    """
    __slots__ = ['id', 'text', 'anotated','tokens', 'root', 'lower_content_tokens', 'dependencies',
                 'named_entities', 'acronyms']

    def __init__(self, num, sentence_text, anotated_sentence, parser_output=None):
        """
        Initialize a sentence from the output of one of the supported parsers. 
        It checks for the tokens themselves, pos tags, lemmas
        and dependency annotations.

        :param parser_output: if None, an empty Sentence object is created.
        """        
        self.id = num  
        self.text = sentence_text        
        self.anotated = anotated_sentence
        self.tokens = []
        self.dependencies = []
        self.root = None
        self.lower_content_tokens = []   
        self.named_entities = []     
        self._extract_dependency_tuples()

    def __str__(self):
        #return ' '.join(str(t) for t in self.tokens)
        return self.text
    
    def __repr__(self):
        repr_str = str(self)
        return repr_str


    def create_fe(self):
        """
        Create the explicit focus list 
        """
        pass


    def create_fi(self):
        """
        Create the implicit focus list 
        """
        pass


    def set_named_entities(self):
        """
        Set named entities of the sentence
        """
        #TODO: Incluir entidades obtidas a partir da DBPedia
        self.named_entities = []
        for entity in self.anotated.ents:
            # each entity is a Span, a sequence of Spacy tokens
            tokens = [self.tokens[spacy_token.i] for spacy_token in entity]
            self.named_entities.append(tokens)


    def _extract_dependency_tuples(self):
        '''
        Extract dependency tuples in the format relation(token1, token2)
        from the sentence tokens.

        These tuples are stored in the sentence object as namedtuples
        (relation, head, modifier). They are stored in a set, so duplicates will
        be lost.
        '''
        self.dependencies = []
        # TODO: use collapsed dependencies
        # (collapse preposition and/or conjunctions)
        for token in self.tokens:
            # ignore punctuation dependencies
            relation = token.dependency_relation
            if relation == 'p':
                continue

            head = token.head
            dep = Dependency(relation, head, token)
            self.dependencies.append(dep)

    def conll_representation(self):
        return self.structure_representation()

    def structure_representation(self):
        """
        Return a CoNLL representation of the sentence's syntactic structure.
        """
        lines = []
        for token in self.tokens:
            head = token.head.id if token.head is not None else 0
            lemma = token.lemma if token.lemma is not None else '_'
            line = '{token.id}\t{token.text}\t{lemma}\t{token.pos}\t_\t_\t' \
                   '{head}\t{token.dependency_relation}' \
                   '' \
                   ''
            line = line.format(token=token, lemma=lemma, head=head)
            lines.append(line)

        return '\n'.join(lines)

    def find_lower_content_tokens(self, stopwords):
        '''
        Store the lower case content tokens (i.e., not in stopwords) for faster
        processing.

        :param stopwords: set
        '''
        self.lower_content_tokens = [token.text.lower()
                                     for token in self.tokens
                                     if token.lemma not in stopwords]


'''    
    def _read_conll_output(self, conll_output):
        """
        Internal function to load data in conll dependency parse syntax.
        """
        lines = conll_output.splitlines()
        sentence_heads = []
        
        for line in lines:
            fields = line.split()
            if len(fields) == 0:
                break

            id_ = int(fields[ConllPos.id])
            word = fields[ConllPos.word]
            pos = fields[ConllPos.pos]
            if pos == '_':
                # some systems output the POS tag in the second column
                pos = fields[ConllPos.pos2]

            lemma = fields[ConllPos.lemma]
            if lemma == '_':
                lemma = lemmatization.get_lemma(word, pos)

            head = int(fields[ConllPos.dep_head])
            dep_rel = fields[ConllPos.dep_rel]
            
            # -1 because tokens are numbered from 1
            head -= 1
            
            token = Token(id_, word, pos, lemma)
            token.dependency_relation = dep_rel

            self.tokens.append(token)
            sentence_heads.append(head)
            
        # now, set the head of each token
        for modifier_idx, head_idx in enumerate(sentence_heads):
            # skip root because its head is -1
            if head_idx < 0:
                self.root = self.tokens[modifier_idx]
                continue
            
            head = self.tokens[head_idx]
            modifier = self.tokens[modifier_idx]
            modifier.head = head
            head.dependents.append(modifier)
'''