
from SingleSentence import SingleSentence


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
        self.text_s1 = s1
        self.text_s2 = s2
        self.lexical_alignments = None
        self.entity_alignments = None
        self.ppdb_alignments = None        
        self.annotated_s1 = None
        self.annotated_s2 = None

        if isinstance(s1, SingleSentence): 
            self.s1 = s1
        elif isinstance(s1, str) or \
            s1 is None:
            self.s1 = SingleSentece(s1)
        else:
            print("Tipo de objeto inválido passado para o construtor: {}".format(type(s1)))

        if isinstance(s2, SingleSentence): 
            self.s2 = s2
        elif isinstance(s2, str) or \
            s2 is None:
            self.s2 = SingleSentece(s2)            
        else:
            print("Tipo de objeto inválido passado para o construtor: {}".format(type(s2)))

        if similarity is not None:
            self.similarity = similarity
    
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
        for entity_s1 in self.annotated_t.named_entities:
            entities_s1.append(preprocess_entity(entity_s1))

        for entity_s2 in self.annotated_h.named_entities:
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

    def find_lexical_alignments(self):
        '''
        Find the lexical alignments in the pair.

        Lexical alignments are simply two equal or synonym words.

        :return: list with the (Token, Token) aligned tuples
        '''
        # pronouns aren't content words, but let's pretend they are
        content_word_tags = {'NOUN', 'VERB', 'PRON', 'ADJ', 'ADV', 'PNOUN'}
        content_words_t = [
            token for token in filter_words_by_pos(
                self.annotated_t.tokens, content_word_tags)
            # own-pt lists ser and ter as synonyms
            if token.lemma not in ['ser', 'ter']]

        content_words_h = [
            token for token in filter_words_by_pos(
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

