from dependency import Dependency
from itertools import permutations
import helper_tools as htools
from collections import defaultdict
import helper_palavras as h_pal

# List of tags of type to compound
# the Explicit Focus entity set
# If using other processor method include PROPN
# FE_POS_TAGS = ["NOUN", "PRON", "PROPN"]
FE_POS_TAGS = ["NOUN", "PRON"]

class SingleSentence(object):
    """
    Class to store a sentence with linguistic annotations.
    """

    __slots__ = ['id', 'text', 'annotated', 'palavras_sentence', 'tokens', 'dependencies', 'root',
                 'lower_content_tokens', 'named_entities', 'dbpedia_mentions_entries',
                 'dbpedia_mentions', 'tokens_dbpedia_metions', 'tokens_fe_pos_tags', 'acronyms', 
                 'list_fe', 'list_fe_li', 'list_fi', 'doc', 'corref_chains']
    
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
        self.corref_chains = set([])
        self.__create_aligned_sentences()
        self.__set_named_entities()
        self._extract_dependency_tuples()
        self.__create_fe()
        self.__create_fe_li()
        self.__create_fi()

        self.__get_corref_chains()

    def __str__(self):
        '''
        String representation
        '''
        
        return self.text

    def __repr__(self):
        '''
        String representation
        '''
        repr_str = str(self)
        return repr_str

    def __get_corref_chains(self):
        '''
        Get all correference chains in the sentence
        '''
        s1_id = self.id+1
        for id_cadeia, cadeia in self.doc.corref_chains.items():            
            if any(str(sn['@sentenca']) == str(s1_id) for sn in cadeia['sn']):
                self.corref_chains.add(id_cadeia)

    def get_token_palavras_tags(self, pal_token, tags='ALL'):
        """
        Retrieve palavras' tags for a token on idx_token
        position

        :param pal_token: VISL token from PALAVRAS
        :param tags: specific tag to filter or all

        :return List of VISL tokens with specific tags 
        """

        if tags == 'ALL':
            return [x[0] for x in pal_token.tags]
        else:
            return [x[0] for x in pal_token.tags if x[1] == tags]

    def get_palavras_tags(self, idx_token, tags='ALL'):
        """
        Retrieve palavras' tags for a token on idx_token
        position

        :param idx_token: VISL id of token

        :return List of VISL tokens position with specific tags 
        """
        l_tokens = [x[1] for x in list(filter(lambda item:
                                              item[1]['spa_start_idx'] == idx_token,
                                              self.aligned_tokens.items()))]

        if tags == 'ALL':
            return [x[0] for y in l_tokens
                    for z in y['pal_tokens'] for x in z.tags]
        else:            
            return [x[0] for y in l_tokens
                         for z in y['pal_tokens']
                         for x in z.tags if x[1] == tags]

    def __create_aligned_sentences(self):
        """
        Create an aligned structure with tokens annotared 
        by palavras and tokens annotated by spacy
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
        it_t_pal = iter(self.palavras_sentence)
        finalizado = False
        while not finalizado:
            try:
                # get PALAVRAS token
                t_pal = next(it_t_pal)

                # tokens that has composition, stay together
                # como em + as = nas, em + o = no
                # PALAVRAS use them separately
                # Ex.: em 	[em] <cjt-head> <sam-> PRP @<ADVL  #8->1
                #      as 	[o] <-sam> <artd> DET F P @>N  #9->10
                if any("<sam->" in tag for tag, _ in t_pal.tags):
                    pal_token_text += t_pal.text+" + "
                    pal_tokens_list.append(t_pal)
                    continue
                elif any("<hyfen>" in tag for tag, _ in t_pal.tags):
                    pal_token_text += t_pal.text+" + "
                    pal_tokens_list.append(t_pal)
                    continue
                else:
                    # first token from palavras
                    pal_token_text += t_pal.text
                    pal_tokens_list.append(t_pal)

                # first token from spacy
                token_spa = next(it_t_spa)
                while h_pal.is_token_punct(token_spa.text):
                    token_spa = next(it_t_spa)

                if "=" in t_pal.text:
                    spa_token_text += token_spa.text
                    spa_tokens_list.append(token_spa)

                    t_num = len(t_pal.text.split('='))

                    for _ in range(t_num-1):
                        token_spa = next(it_t_spa)
                        spa_token_text += " + "+token_spa.text
                        spa_tokens_list.append(token_spa)
                else:
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
                                             'spa_text': spa_token_text,
                                             'pal_tokens': pal_tokens_list,
                                             'spa_tokens': spa_tokens_list,
                                             'pal_start_idx': pal_idx_token,
                                             'spa_start_idx': spa_idx_token}
                idx_token += 1
                pal_idx_token += len(pal_tokens_list)
                spa_idx_token += len(spa_tokens_list)
                pal_token_text = ""
                spa_token_text = ""
                pal_tokens_list = []
                spa_tokens_list = []

            except StopIteration:
                finalizado = True

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
                        v['raw_text']] = self.annotated[t.i:t.i+offset]
            
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
            if lemma_fe_elem is None or\
               len(lemma_fe_elem.strip()) == 0:  # Não foi encontrado token equivalente
                lemma_fe_elem = fe_elem
            
            fe_li_synms = set(htools.dic_tep2.get_sinonimos(lemma_fe_elem))
            
            if len(fe_li_synms) == 0:
                continue

            if lemma_fe_elem in self.list_fe_li.keys():
                self.list_fe_li[lemma_fe_elem] = self.list_fe_li[lemma_fe_elem].union(fe_li_synms)
            else:
                self.list_fe_li[lemma_fe_elem] = fe_li_synms
        
    def show_list_fe(self):
        '''
        Display explicit focus list
        '''
        for fe_elem in self.list_fe:
            print(fe_elem)

    def __create_fi(self):
        """
        Create the implicit focus list 
        """
        # Append entities like nouns, proper nouns
        # and pronouns and get their semantic tags

        for aligned_token in self.aligned_tokens.values():
            if len(aligned_token['spa_tokens']) == 1:
                spa_token = aligned_token['spa_tokens'][0]    
                if spa_token.pos_ in FE_POS_TAGS:
                    tags = []
                    for pal_token in aligned_token['pal_tokens']:
                        tags = self.get_token_palavras_tags(pal_token,
                                                            tags='SEMANTIC')
                        if len(tags) > 0:
                            self.list_fi[spa_token.text] = tags
        

    def __set_named_entities(self):
        """
        Set named entities of the sentence
        """
        # TODO: include entities from DBPedia
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
        '''
        Get conll representation
        Check: Code use from infernal code

        :return Structure representation
        '''
        return self.structure_representation()

    def structure_representation(self):
        """
        Return a CoNLL representation of the sentence's syntactic structure.

        :return str Text of all lines concatenated with break line
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

        :param set stopwords: set of stop words considered
        '''
        self.lower_content_tokens = [token.text.lower()
                                     for token in self.tokens
                                     if token.lemma not in stopwords]

