#!/usr/bin/env python3

import sys
import re

def format_tree(): #converts from Penn Treebank to Stanford output
    regex = re.compile(r"\(([A-Za-z_$]+)")
    with open(sys.argv[1]) as np_lines:
        for line in np_lines:
            print(regex.sub(r"\1(", line), end="")

format_tree()
