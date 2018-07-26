from nltk.corpus import treebank

for n in range(1,200): 
    tree_file = "wsj_{}.mrg".format(str(n).zfill(4))
    sentences = treebank.parsed_sents(tree_file)
    for s in sentences:
        for subtree in s.subtrees(lambda t: t.label().startswith("NP")):
            print(subtree)
