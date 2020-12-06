
class Token(object):
    """
    Simple data container class representing a token and its linguistic
    annotations.
    """
    __slots__ = ['id', 'text', 'pos', 'lemma', 'head', 'dependents',
                 'dependency_relation', 'dependency_index', 'word_index']

    def __init__(self, num, text, pos=None, lemma=None):
        self.id = num  # sequential id in the sentence
        self.text = text
        self.pos = pos
        self.lemma = lemma
        self.dependents = []
        self.dependency_relation = None
        self.dependency_index = None
        self.word_index = None

        # Token.head points to another token, not an index
        self.head = None

    def __repr__(self):
        repr_str = '<Token %s, Dep rel=%s>' % (self.text,
                                               self.dependency_relation)
        return repr_str

    def __str__(self):
        return self.text

    def get_dependent(self, relation, error_if_many=False):
        """
        Return the modifier (syntactic dependents) that has the specified
        dependency relation. If `error_if_many` is true and there is more
        than one have the same relation, it raises a ValueError. If there
        are no dependents with this relation, return None.

        :param relation: the name of the dependency relation
        :param error_if_many: whether to raise an exception if there is
            more than one value
        :return: Token
        """
        deps = [dep for dep in self.dependents
                if dep.dependency_relation == relation]

        if len(deps) == 0:
            return None
        elif len(deps) == 1 or not error_if_many:
            return deps[0]
        else:
            msg = 'More than one dependent with relation {} in token {}'.\
                format(relation, self)
            raise ValueError(msg)

    def get_dependents(self, relation):
        """
        Return modifiers (syntactic dependents) that have the specified dependency
        relation.

        :param relation: the name of the dependency relation
        """
        deps = [dep for dep in self.dependents
                if dep.dependency_relation == relation]

        return deps
