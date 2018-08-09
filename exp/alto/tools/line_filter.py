#!/usr/bin/env python3

import sys

def line_filter():
    seen = set()
    with open(sys.argv[1]) as np_doc:
        for line in np_doc:
            if line not in seen:
                seen.add(line)
                print(line, end="")

  

line_filter()
