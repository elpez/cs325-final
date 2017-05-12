"""
Demonstration of a simple ADJ N -> N ADJ transformation
>>> switch_n_ad = Transform(['aq', 'n'], ['n', 'aq'])
>>> tree = Tree('S', [('big', 'aq'), Tree('n', [('green', 'aq'), ('flowers', 'n')])])
>>> new_tree = switch_n_ad(tree)
>>> print new_tree
(S (n flowers/n green/aq) big/aq)
"""
from nltk.tree import Tree

class Transform(object):
    def __init__(self, match, change):
        if any(rule not in match for rule in change):
            raise ValueError('change pattern cannot add rules')
        self.match = match
        self.change = change

    def __call__(self, tree):
        """Apply the transformation recursively to the tree."""
        if not isinstance(tree, Tree):
            return tree
        ret = [''] * len(self.change)
        children = map(get_label, tree)
        if children == self.match:
            for child in tree:
                try:
                    # find where the node is supposed to go in the output
                    insert_index = self.change.index(get_label(child))
                    ret[insert_index] = child
                except ValueError:
                    # this just indicates that the given leaf is deleted
                    pass
            return Tree(tree.label(), map(self, ret))
        else:
            childTrees = []
            for child in tree:
                childTrees += [child]
            return Tree(tree.label(), map(self, childTrees))

def get_label(tree_or_leaf):
    """Get the label of the tree or leaf, assuming that if it is a leaf it is a (word, POS) tuple.
    """
    if isinstance(tree_or_leaf, Tree):
        return tree_or_leaf.label()
    else:
        return tree_or_leaf[1]

# adjectives come after nouns
transforms = [(['n', 'a'], ['a', 'n']), (['grup.verb','grup.nom'],['grup.nom','grup.verb'])]

def syntactic_transfer(tree):
    if isinstance(tree, Tree):
        newTree = tree
        for trans in transforms:
	    transform = Transform(trans[0],trans[1])
            newTree = transform(newTree)
    else: #list of tuples
        prevWord = ('','')
        newTree = []
        for word in tree:
            transformed_word = False
            for transform in transforms:
                if prevWord[1] == transform[0][0] and word[1] == transform[0][1] and not transformed_word:
                    toAdd = [word,prevWord]
                    transformed_word = True
                elif not transformed_word:
                    toAdd = [prevWord]
            newTree += toAdd
            prevWord = word
    return newTree

if __name__ == '__main__':
    import doctest
    doctest.testmod()
