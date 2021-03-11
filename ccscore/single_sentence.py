
from dependency import Dependency
from itertools import permutations
import helper_tools as htools
from tep2 import GrupoSinonimo
from infernal import openwordnetpt as own
from collections import defaultdict

# Lista das etiquetas dos tipos que irão compor
# a lista de entidades do Foco Explícito
# substantivos, pronomes, nomes próprios
# FE_POS_TAGS = ["NOUN", "PRON", "PROPN"]
FE_POS_TAGS = ["NOUN", "PRON"]

class SingleSentence(object):
    """
    Class to store a sentence with linguistic annotations.
    """
    #__slots__ = ['id', 'text', 'annotated','tokens', 'dependencies', 'root', 'lower_content_tokens', 
    #             'named_entities', 'dbpedia_mentions_entries', 'dbpedia_mentions', 'acronyms', 'list_fe', 'list_fi',
    #             'doc']

    def __init__(self, num, sentence_text, annotated_sentence=None, doc=None,
                 parser_output=None, palavras_sentence=None):
        """
        Initialize a sentence from the output of one of the supported parsers. 
        It checks for the tokens themselves, pos tags, lemmas
        and dependency annotations.

        :param parser_output: if None, an empty Sentence object is created.
        """
        self.id = num
        self.text = sentence_text
        self.annotated = annotated_sentence
        self.palavras_sentence = palavras_sentence
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
        self.list_fe_li = {}
        self.list_fi = {}
        self.doc = doc
        self.__create_aligned_sentences()
        self.__set_named_entities()
        self._extract_dependency_tuples()
        self.__create_fe()
        self.__create_fe_li()
        self.__create_fi()

    def __str__(self):
        # return ' '.join(str(t) for t in self.tokens)
        return self.text

    def __repr__(self):
        repr_str = str(self)
        return repr_str

    def get_palavras_tags(self, idx_token, tags='ALL'):
        """
        Retrieve palavras' tags for a token on idx_token 
        position
        """
        l_tokens = [x[1] for x in list(filter(lambda item:
                                              item[1]['spa_start_idx'] == idx_token,
                                              self.aligned_tokens.items()))]

        if tags == 'ALL':
            return [x[0] for y in l_tokens
                    for z in y['pal_tokens'] for x in z.tags]
        else:
            # return [x[0] for y in
            #        self.aligned_tokens[idx_token]['pal_tokens'] for x in y.tags
            #        if x[1] == tags]

            return [x[0] for y in l_tokens
                            for z in y['pal_tokens'] 
                                for x in z.tags if x[1] == tags]


    def __create_aligned_sentences(self):
        """
        Create an structure with tokens annotared by palavras
        and tokens annotated by spacy, aligned. 
        """
        aligned_tokens = defaultdict()
        idx_token = 0
        pal_idx_token = 0
        spa_idx_token = 0
        pal_token_text = ""
        spa_token_text = ""
        pal_tokens_list = []
        spa_tokens_list = []
        it_t_spa = iter(self.annotated)
        for t_pal in self.palavras_sentence:   
            
            # tokens that has composition, stay together    
            if any("<sam->" in tag for tag,_ in t_pal.tags):
                pal_token_text += t_pal.text+" + " 
                pal_tokens_list.append(t_pal)    
                continue
            else:
                # first token from palavras
                pal_token_text += t_pal.text
                pal_tokens_list.append(t_pal)

            # first token from spacy
            token_spa = next(it_t_spa)
            spa_token_text += token_spa.text
            spa_tokens_list.append(token_spa)

            # tokens of proper names are grouped in palavras but,
            # in spacy not
            if " " in t_pal.text:
                for _ in range(len(t_pal.text.split(' '))-1):
                    token_spa = next(it_t_spa)
                    spa_token_text += " "+token_spa.text
                    spa_tokens_list.append(token_spa)

            aligned_tokens[idx_token] = {'text': pal_token_text,
                                         'pal_tokens': pal_tokens_list,
                                         'spa_tokens': spa_tokens_list,
                                         'pal_start_idx': pal_idx_token,
                                         'spa_start_idx': spa_idx_token
                                        }
            idx_token += 1
            pal_idx_token += len(pal_tokens_list)
            spa_idx_token += len(spa_tokens_list)
            pal_token_text = ""
            spa_token_text = ""
            pal_tokens_list = []
            spa_tokens_list = []

        self.aligned_tokens = aligned_tokens

    def __create_fe(self):
        """
        Create the explicit focus list
        """
        # Append entities like nouns, proper nouns
        # and pronouns

        for token in self.annotated:
            if token.pos_ in FE_POS_TAGS:
                # token_text = token.text.lower()
                token_text = token.text
                self.tokens_fe_pos_tags[token_text] = token
                self.list_fe.append(token_text)

        # Append named entities
        for ne in self.named_entities:
            # self.list_fe.append(ne.text.lower())
            self.list_fe.append(ne.text)

        # Get named entities marked by DBpedia Spotlight
        self.dbpedia_mentions_entries = htools.get_dbpedia_entries(self.text)

        for k, v in self.dbpedia_mentions_entries.items():
            self.dbpedia_mentions.append(k)
            for t in self.annotated:
                if t.idx == int(v['pos']):
                    offset = len(v['raw_text'].split())
                    self.tokens_dbpedia_metions[
                        # v['raw_text'].lower()] = self.annotated[t.i:t.i+offset]
                        v['raw_text']] = self.annotated[t.i:t.i+offset]

            # self.list_fe.append(v['raw_text'].lower())
            self.list_fe.append(v['raw_text'])

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
        # own.load_wordnet("./data/own-pt.pickle")
        # WordNet não será usada aqui
        
        # Find all synonyms of explicit focus list
        for fe_elem in self.list_fe:
            fe_li_synms = set([])

            # Do not search synonyms for proper names
            if fe_elem in self.tokens_fe_pos_tags.keys() and \
               self.tokens_fe_pos_tags[fe_elem].pos_ == "PROPN":
                continue

            # Do not search synonyms for named entities
            # and dbpedia_mentions
            # if fe_elem in self.named_entities or \
            if any(fe_elem.lower() == x.lower() for x in self.dbpedia_mentions) or \
               any(fe_elem.lower() == x.text.lower() for x in self.named_entities):
                continue
            
            lemma_fe_elem = None
            lemma_fe_elem = htools.cogroo_lemmatize(fe_elem)
            if lemma_fe_elem is None:  # Não foi encontrado token equivalente
                lemma_fe_elem = fe_elem

            # fe_li_synms = fe_li_synms.union(own.find_synonyms(lemma_fe_elem))
            # Do not use synsets here. When comparing semantic tags of elements
            # of FE_LI we can will use the function are_synonyms.
            fe_li_synms = set(htools.dic_tep2.get_sinonimos(lemma_fe_elem))
            
            if len(fe_li_synms) == 0:
                continue

            if lemma_fe_elem in self.list_fe_li.keys():
                self.list_fe_li[lemma_fe_elem] = self.list_fe_li[lemma_fe_elem].union(fe_li_synms)
            else:
                self.list_fe_li[lemma_fe_elem] = fe_li_synms
            
        # self.list_fe_li = list(fe_li_synms.union(set(self.list_fe)))

    def show_list_fe(self):
        for fe_elem in self.list_fe:
            print(fe_elem)


    def __create_fi(self):
        """
        Create the implicit focus list 
        """
        # Append entities like nouns, proper nouns
        # and pronouns and get their semantic tags

        for idx_token, token in enumerate(self.annotated):
            if token.pos_ in FE_POS_TAGS:
                tags = self.get_palavras_tags(idx_token, tags='SEMANTIC')
                if len(tags) > 0:
                    self.list_fi[token.text] = tags

    def __set_named_entities(self):
        """
        Set named entities of the sentence
        """
        # TODO: Incluir entidades obtidas a partir da DBPedia
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