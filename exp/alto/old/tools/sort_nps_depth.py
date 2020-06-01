#!/usr/bin/env python3

import sys
from nltk.tree import Tree

def sort_nps():
    with open(sys.argv[1]) as np_doc:
        for line in np_doc:
            np = Tree.fromstring(line)
            print(np.height(), line, end ="")

sort_nps()
