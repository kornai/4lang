from nltk.corpus import treebank

from common import sanitize_word

def format_tree(tree):
    if tree.height() == 2: #word, pos
        tree[0] = sanitize_word(tree[0]) #tree[0] == word
    else:
        for subtree in tree:
            format_tree(subtree)


for n in range(1,200): 
    tree_file = "wsj_{}.mrg".format(str(n).zfill(4))
    sentences = treebank.parsed_sents(tree_file)
    for s in sentences:
        for subtree in s.subtrees(lambda t: t.label() == "NP"):
            format_tree(subtree)
            print(subtree.pformat(100000))
            #print(subtree)
