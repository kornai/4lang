#!/usr/bin/env python
# *-* coding=utf-8 *-*

# Compares the nolarge.graphs file (the one without #-lines) and Alto's output to find sentences that cannot be parsed

import sys
from itertools import izip
import re

def find_nulls(fn1, fn2): 
    with open(sys.argv[1]) as nolarge_graphs, open (sys.argv[2]) as alto_output: 
        for x, y, z in izip(nolarge_graphs, alto_output, alto_output):
            if re.search("^(<null>|null)", y):
                x = x.strip()
                z = y.strip()
                print("{0}\n{1}\n{2}".format(x, z, ''))

find_nulls(sys.argv[1], sys.argv[2])
