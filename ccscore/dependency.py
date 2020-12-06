

class Dependency(object):
    """
    Class to store data about a dependency relation and provide
    methods for comparison
    """
    __slots__ = 'label', 'head', 'dependent'

    equivalent_labels = {('nsubjpass', 'dobj'), ('dobj', 'nsubjpass')}

    def __init__(self, label, head, dependent):
        self.label = label
        self.head = head
        self.dependent = dependent

    def get_data(self):
        head = self.head.lemma if self.head else None
        return self.label, head, self.dependent.lemma

    def __repr__(self):
        s = '{}({}, {})'.format(*self.get_data())
        return s

    def __hash__(self):
        return hash(self.get_data())

    def __eq__(self, other):
        """
        Check if the lemmas of head and modifier are the same across
        two Dependency objects.
        """
        if not isinstance(other, Dependency):
            return False
        return self.get_data() == other.get_data()

    def is_equivalent(self, other):
        """
        Return True if this dependency and the other have the same label and
        their three components either have the same lemma or are synonyms.

        :param other: another dependency instance
        :return: boolean
        """
        eq_label = (self.label, other.label) in self.equivalent_labels
        if not eq_label and self.label != other.label:
            return False

        lemma1 = self.head.lemma if self.head else None
        lemma2 = other.head.lemma if other.head else None
        if lemma1 != lemma2 and not own.are_synonyms(lemma1, lemma2):
            return False

        lemma1 = self.dependent.lemma
        lemma2 = other.dependent.lemma
        if lemma1 != lemma2 and not own.are_synonyms(lemma1, lemma2):
            return False

        return True
