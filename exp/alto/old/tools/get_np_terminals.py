import sys

from nltk.tree import Tree

TEMPLATE = ('{0} -> {1}_{0}\n[tree] {0}({1})\n[ud] "({1}<root> / {1})"\n' +
'[fourlang] "({1}<root> / {1})"\n')

def get_np_terminals():
    seen = set()
    with open(sys.argv[1]) as trees:
        for tree in trees:
            tree =  Tree.fromstring(tree)
            pos_list = tree.pos()
            for pos in pos_list:
                if pos not in seen:
                    seen.add(pos)

    #print(seen)
    for tuples in seen:
         print TEMPLATE.format(tuples[1], tuples[0])

  
get_np_terminals()
