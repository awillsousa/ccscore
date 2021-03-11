
from single_sentence import SingleSentence
import helper_palavras as hpal
import helper_tools as htools
from itertools import product
from infernal import openwordnetpt as own
from infernal import ppdb


content_word_tags = {'NOUN', 'VERB', 'ADJ', 'ADV', 'PNOUN'}

class SentencePair(object):
    """
    Class representing a pair of sentences
    """
    def __init__(self, s1, s2, similarity=None):
        """
        :param s1: the first sentence as a string
        :param s2: the second sentence as a string                
        :param similarity: similarity score as a float
        """
        self.s1 = s1
        self.s2 = s2
        self.fe_intersection = self.get_fe_intersection()
        self.fi_intersection = self.get_fi_intersection()
        self.lexical_alignments = None
        self.entity_alignments = None
        self.ppdb_alignments = None
        # self.annotated_s1 = None
        # self.annotated_s2 = None

        if isinstance(s1, SingleSentence): 
            self.s1 = s1
        elif isinstance(s1, str) or s1 is None:
            self.s1 = SingleSentece(s1)
        else:
            print("Tipo de objeto inválido passado para o construtor: {}".format(type(s1)))
            raise(TypeError)

        if isinstance(s2, SingleSentence): 
            self.s2 = s2
        elif isinstance(s2, str) or \
            s2 is None:
            self.s2 = SingleSentece(s2)            
        else:
            print("Tipo de objeto inválido passado para o construtor: {}".format(type(s2)))
            raise(TypeError)

        if similarity is not None:
            self.similarity = similarity

        

    def get_fe_intersection(self):
        """
        Get the intersection of explicit focus list
        of the pairs' sentences
        """
        s1_list_fe = self.s1.list_fe
        s2_list_fe = self.s2.list_fe
        from_li_le = {}

        for elem_s1 in self.s1.list_fe:
            if elem_s1 in self.s1.list_fe_li.keys():
                for sinon_elem_s1 in self.s1.list_fe_li[elem_s1]:
                    for elem_s2 in self.s2.list_fe:
                        if sinon_elem_s1 == elem_s2:
                            tag_elem_s1 = self.s1.list_fi[elem_s1]
                            tag_sinon_in_s2 = self.s2.list_fi[elem_s2]

                            if tag_elem_s1 == tag_sinon_in_s2:
                                from_li_le.add(sinon_elem_s1)

        return (set(self.s1.list_fe).union(from_li_le)).intersection(set(self.s2.list_fe))

    def get_fi_intersection(self):
        """
        Get the intersection of implicit focus list
        of the pair's sentences
        """
        reduced_list_fi = {k: v for k, v in self.s1.list_fi.items()
                           if k not in self.fe_intersection}


        result_list_fi = (set([y for x in reduced_list_fi.values() for y in x]).intersection(
                          set(y for x in self.s2.list_fi.values() for y in x)))

        if len(result_list_fi) == 0:
            return self.get_mininal_fi_intersection()
        else:
            return result_list_fi

    def get_mininal_fi_intersection(self):
        """
        When Intersection between explicit focus of
        the two sentences, try to establish a minimal
        relationship, comparing if the two sentences
        share the same umbrella category tag
        """
        s1_fi_elems = set([y for x in self.s1.list_fi.values() for y in x])
        s2_fi_elems = set([y for x in self.s2.list_fi.values() for y in x])
        min_fi_elems = {}
        for el1, el2 in product(s1_fi_elems, s2_fi_elems):
            common_substr = htools.longest_common_substr([el1, el2])

            if not(common_substr is None) and \
               common_substr[0] == '<':
                tag = f"{common_substr}>"
                if hpal.is_umbrella(tag):
                    min_fi_elems.add(tag)

        return min_fi_elems

    def calc_local_cohesion(self):
        """
        Analyze explicit and implicit focus relations and 
        return a value based on combinations of their values. 
        """
        fi1_C_fi2 = len(self.fi_intersection) > 0
        fi1_NC_fi2 = not(fi1_C_fi2)
        fe1_C_fe2 = len(self.fe_intersection) > 0
        fe1_NC_fe2 = not(fe1_C_fe2)

        if fi1_C_fi2 and fe1_C_fe2:
            return 1.0           # Elaboration
        elif fi1_NC_fi2 and fe1_C_fe2:
            return 0.75          # Keep on topic
        elif fi1_C_fi2 and fe1_NC_fe2:
            return 0.50          # Topic change
        elif fi1_NC_fi2 and fe1_NC_fe2:
            return 0.0           # Subject change


    def find_entity_alignments(self):
        """
        Find named entities aligned in the two sentences.

        This function checks full forms and acronyms.
        """
        def preprocess_entity(entity):
            if len(entity) > 1:
                acronym = ''.join([token.text[0].lower() for token in entity
                                   if token.text[0].isupper()])
            else:
                acronym = None

            # remove dots from existing acronyms
            words = [token.text.replace('.', '').lower() for token in entity]

            return entity, words, acronym

        entities_s1 = []
        entities_s2 = []
        self.entity_alignments = []
        for entity_s1 in self.s1.named_entities:
            entities_s1.append(preprocess_entity(entity_s1))

        for entity_s2 in self.s2.named_entities:
            entities_s2.append(preprocess_entity(entity_s2))

        for entity_s1, words_t, acronym_t in entities_s1:

            for entity_s2, words_h, acronym_h in entities_s2:
                # if both entities have more than one word, compare them and not
                # their acronyms; this avoids false positives when only initials
                # match
                # same goes if both are single words; there are no acronyms
                both_mult = len(entity_s1) > 1 and len(entity_s2) > 1
                both_single = len(entity_s1) == 1 and len(entity_s2) == 1
                if both_mult or both_single:
                    if words_t == words_h:
                        self.entity_alignments.append((entity_s1, entity_s2))
                    else:
                        continue

                # the remaining case is one is a single word and the other has
                # many. Check one against the acronym of the other.
                if len(entity_s1) > 1:
                    if acronym_t == words_h[0]:
                        self.entity_alignments.append((entity_s1, entity_s2))
                else:
                    if acronym_h == words_t[0]:
                        self.entity_alignments.append((entity_s1, entity_s2))

    def find_ppdb_alignments(self, max_length):
        """
        Find lexical and phrasal alignments in the pair according to
        transformation rules from the paraphrase database.

        This function should only be called after annotated_t and annotated_h
        have been provided.

        :param max_length: maximum length of the left-hand side (in number of
            tokens)
        """
        tokens_s1 = self.annotated_t.tokens
        tokens_s2 = self.annotated_h.tokens
        token_texts_s1 = [token.text.lower() for token in tokens_s1]
        token_texts_s2 = [token.text.lower() for token in tokens_s2]
        alignments = []

        # for purposes of this function, treat pronouns as content words
        global content_word_tags

        for i, token in enumerate(tokens_s1):
            # check the maximum length that makes sense to search for
            # (i.e., so it doesn't go past sentence end)
            max_possible_length = min(len(tokens_s1) - i, max_length)
            for length in range(1, max_possible_length):
                if length == 1 and token.pos not in content_word_tags:
                    continue

                lhs = [token for token in token_texts_s1[i:i + length]]
                rhs_rules = ppdb.get_rhs(lhs)
                if not rhs_rules:
                    continue

                # now get the token objects, instead of just their text
                lhs = tokens_s1[i:i + length]

                for rule in rhs_rules:
                    index = ppdb.search(token_texts_s2, rule)
                    if index == -1:
                        continue
                    alignment = (lhs, tokens_s2[index:index + len(rule)])
                    alignments.append(alignment)

        self.ppdb_alignments = alignments

    def filter_words_by_pos(self, tokens, tags=None):
        """
        Filter out words based on their POS tags.

        If no set of tags is provided, a default of content tags is used:
        {'NOUN', 'VERB', 'ADJ', 'ADV', 'PNOUN'}

        :param tokens: list of datastructures.Token objects
        :param tags: optional set of allowed tags
        :return: list of the tokens having the allowed tokens
        """
        if tags is None:
            tags = content_word_tags

        return [token for token in tokens if token.pos in tags]

    def find_lexical_alignments(self):
        '''
        Find the lexical alignments in the pair.

        Lexical alignments are simply two equal or synonym words.

        :return: list with the (Token, Token) aligned tuples
        '''
        # pronouns aren't content words, but let's pretend they are
        content_word_tags = {'NOUN', 'VERB', 'PRON', 'ADJ', 'ADV', 'PNOUN'}
        content_words_t = [
            token for token in self.filter_words_by_pos(
                self.annotated_t.tokens, content_word_tags)
            # own-pt lists ser and ter as synonyms
            if token.lemma not in ['ser', 'ter']]

        content_words_h = [
            token for token in self.filter_words_by_pos(
                self.annotated_h.tokens, content_word_tags)
            if token.lemma not in ['ser', 'ter']]

        lexical_alignments = []

        for token_t in content_words_t:
            nominalizations_t = own.find_nominalizations(token_t.lemma)

            for token_h in content_words_h:
                aligned = False
                if token_t.lemma == token_h.lemma:
                    aligned = True
                elif own.are_synonyms(token_t.lemma, token_h.lemma):
                    aligned = True
                elif token_h.lemma in nominalizations_t:
                    aligned = True
                elif token_t.lemma in own.find_nominalizations(token_h.lemma):
                    aligned = True

                if aligned:
                    lexical_alignments.append((token_t, token_h))

        self.lexical_alignments = lexical_alignments

