from itertools import combinations
from sentence_pair import SentencePair
import ccscore_exceptions as ccExcept


class SingleParagraph(object):
    """
    Class to store a paragraph
    """
    # __slots__ = ['id', 'text', 'sentences', 'list_fe', 'list_fi', 'doc']

    def __init__(self, num, paragraph_text, sentences_id=[], doc=None):
        """
        Initialize a sentence from the output of one of the supported parsers.
        It checks for the tokens themselves, pos tags, lemmas
        and dependency annotations.

        :param parser_output: if None, an empty Sentence object is created.
        """
        self.id = num
        self.text = paragraph_text
        self.sentences_id = sentences_id
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

    def get_sentences(self):
        return [s for s in self.doc.sentences if s.id in self.sentences_id]

    def __create_fe(self):
        """
        Create the explicit focus list for paragraphs
        using maximum adjacency between sentences of
        the paragraph.
        Explicit Focus List will be:
        FE = UNION( INTERSECTION(s1.fe,s2.fe),INTERSECTION(s1.fe,s3.fe),...,INTERSECTION(s1.fe,sN.fe),
                    INTERSECTION(s2.fe,s3.fe),INTERSECTION(s3.fe,s4.fe),...,INTERSECTION(s2.fe,sN.fe),
                    ..., INTERSECTION(sN-1.fe,sN.fe)
                  )
        """
        # sents = [s for s in self.doc.sentences if s.id in self.sentences_id]
        sents = self.get_sentences()
        fe_pairs = []
        if len(sents) > 1:
            for s1, s2 in combinations(sents, 2):
                fe_pairs.append(set(SentencePair(s1, s2).fe_intersection))

            if len(fe_pairs) == 0:
                self.list_fe = set([])
            else:
                self.list_fe = set.union(*fe_pairs)

        elif len(sents) == 1:
            self.list_fe = sents[0].list_fe
        else:
            raise ccExcept.EmptyParagraph

    def __create_fi(self):
        """
        Create the implicit focus list for paragraphs
        using maximum adjacency between sentences of
        the paragraph.
        Implicit Focus List will be:
        FI = UNION( INTERSECTION(s1.fi,s2.fi),INTERSECTION(s1.fi,s3.fi),...,INTERSECTION(s1.fi,sN.fi),
                    INTERSECTION(s2.fi,s3.fi),INTERSECTION(s3.fi,s4.fi),...,INTERSECTION(s2.fi,sN.fi),
                    ..., INTERSECTION(sN-1.fi,sN.fi)
                  )
        """
        # sents = [s for s in self.doc.sentences if s.id in self.sentences_id]
        sents = self.get_sentences()
        fi_pairs = []
        if len(sents) > 1:
            for s1, s2 in combinations(sents, 2):
                fi_pairs.append(set(SentencePair(s1, s2).fi_intersection))

            fi_elems = {}
            if len(fi_pairs) > 0:
                list_fi = set.union(*fi_pairs)
                for sentence in sents:
                    for elem_fi_token, elem_fi_tags in sentence.list_fi.items():
                        if any(x in list_fi for x in elem_fi_tags):
                            fi_elems[elem_fi_token] = elem_fi_tags

            self.list_fi = fi_elems
        elif len(sents) == 1:
            self.list_fi = sents[0].list_fi
        else:
            raise ccExcept.EmptyParagraph
