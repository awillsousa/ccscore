
from dependency import Dependency
from itertools import permutations
import helper_tools as htools
from tep2 import GrupoSinonimo
from infernal import openwordnetpt as own

# Lista das etiquetas dos tipos que irão compor
# a lista de entidades do Foco Explícito
# substantivos, pronomes, nomes próprios
FE_POS_TAGS = ["NOUN", "PRON", "PROPN"] 

class SingleSentence(object):
    """
    Class to store a sentence with linguistic annotations.
    """
    #__slots__ = ['id', 'text', 'annotated','tokens', 'dependencies', 'root', 'lower_content_tokens', 
    #             'named_entities', 'dbpedia_mentions_entries', 'dbpedia_mentions', 'acronyms', 'list_fe', 'list_fi',
    #             'doc']

    def __init__(self, num, sentence_text, annotated_sentence=None, doc=None, parser_output=None):
        """
        Initialize a sentence from the output of one of the supported parsers. 
        It checks for the tokens themselves, pos tags, lemmas
        and dependency annotations.

        :param parser_output: if None, an empty Sentence object is created.
        """
        self.id = num
        self.text = sentence_text
        self.annotated = annotated_sentence
        self.tokens = []
        self.dependencies = []
        self.root = None
        self.lower_content_tokens = []
        self.named_entities = []
        self.dbpedia_mentions_entries = []
        self.dbpedia_mentions = []
        self.tokens_dbpedia_metions = {}
        self.tokens_fe_pos_tags = {}
        self.acronyms = []
        self.list_fe = []
        self.list_fe_li = []
        self.list_fi = []
        self.doc = doc
        self.__set_named_entities()
        self._extract_dependency_tuples()
        self.__create_fe()
        self.__create_fe_li()

    def __str__(self):
        #return ' '.join(str(t) for t in self.tokens)
        return self.text

    def __repr__(self):
        repr_str = str(self)
        return repr_str

    def __create_fe(self):
        """
        Create the explicit focus list
        """
        # Append entities like nouns, proper nouns
        # and pronouns

        for token in self.annotated:
            if token.pos_ in FE_POS_TAGS:
                token_text = token.text.lower()
                self.tokens_fe_pos_tags[token_text] = token
                self.list_fe.append(token_text)

        # Append named entities
        for ne in self.named_entities:
            self.list_fe.append(ne.text.lower())

        # Get named entities marked by DBpedia Spotlight
        self.dbpedia_mentions_entries = htools.get_dbpedia_entries(self.text)

        for k, v in self.dbpedia_mentions_entries.items():
            self.dbpedia_mentions.append(k)
            for t in self.annotated:
                if t.idx == int(v['pos']):
                    offset = len(v['raw_text'].split())
                    self.tokens_dbpedia_metions[v['raw_text'].lower()] = self.annotated[t.i:t.i+offset]

            self.list_fe.append(v['raw_text'].lower())

        # Create the list as a set, excluding repetead elements
        self.list_fe = list(set(self.list_fe))

        # Now we need to exclude, elements that are contained in others
        it_fe_pairs = permutations(self.list_fe, 2)
        elems_to_exclude = set([])
        for a, b in it_fe_pairs:
            if len(a.split()) == 1:
                if a in b:
                    elems_to_exclude.add(a)
        self.list_fe = list(set(self.list_fe).difference(set(elems_to_exclude)))

    def __create_fe_li(self):
        """
        Create an intermediate list of entities related to Explicit Focus (FE) list,
        using synonyms of element from FE
        """

        # Wordnet load. It's execute just one time (using a global)
        own.load_wordnet("./data/own-pt.pickle")
        fe_li_synms = set([])
        # Find all synonyms of explicit focus list
        for fe_elem in self.list_fe:
            
            # Do not search synonyms for proper names
            if fe_elem in self.tokens_fe_pos_tags.keys() and \
                self.tokens_fe_pos_tags[fe_elem].pos_ == "PROPN":
                continue
            
            lemma_fe_elem = None
            lemma_fe_elem = htools.cogroo_lemmatize(fe_elem)
            if lemma_fe_elem is None:  # Não foi encontrado token equivalente
                lemma_fe_elem = fe_elem

            fe_li_synms = fe_li_synms.union(own.find_synonyms(lemma_fe_elem))
            fe_li_synms = fe_li_synms.union(set(htools.dic_tep2.get_sinonimos(lemma_fe_elem)))
            
        self.list_fe_li = list(fe_li_synms.union(set(self.list_fe)))

    def show_list_fe(self):
        for fe_elem in self.list_fe:
            print(fe_elem)


    def __create_fi(self):
        """
        Create the implicit focus list 
        """
        pass


    def __set_named_entities(self):
        """
        Set named entities of the sentence
        """
        #TODO: Incluir entidades obtidas a partir da DBPedia
        self.named_entities = []        
        # each entity is a Span, a sequence of Spacy tokens            
        self.named_entities.extend(self.annotated.ents)

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