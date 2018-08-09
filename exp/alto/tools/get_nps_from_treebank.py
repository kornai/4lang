import sys

from nltk.corpus import treebank

from common import REPLACE_MAP
from common import sanitize_word

def sanitize_label(tree): #sanitize labels which contain hyphens (e.g.NP-SBJ)
    tree.set_label(tree.label().replace("-", "_"))

def sanitize_pos(tree): #replace punctuation pos-tags
    tree_label = tree.label()
    is_punct = True
    for character in tree_label:
        if character not in REPLACE_MAP:
            is_punct = False
    if is_punct == True:
        tree.set_label("PUNCT") 


def sanitize_tree(tree):
    sanitize_label(tree)
    if tree.height() == 2: #word, pos
        sanitize_pos(tree)        
        tree[0] = sanitize_word(tree[0]) #tree[0] == word
    else:
        for subtree in tree:
            sanitize_tree(subtree)

sanitize = False
if len(sys.argv) > 1 and sys.argv[1] == "sanitize": #pass "sanitize" as 1st argument to sanitize the leaves
    sanitize = True
for n in range(1,200): 
    tree_file = "wsj_{}.mrg".format(str(n).zfill(4))
    sentences = treebank.parsed_sents(tree_file)
    for s in sentences:
        for subtree in s.subtrees(lambda t: t.label() == "NP"):
            if sanitize == True:
                sanitize_tree(subtree)
            print(subtree.pformat(100000))
            break
            #print(subtree)
