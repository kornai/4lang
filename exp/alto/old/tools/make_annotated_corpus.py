#!/usr/bin/env python
# *-* coding=utf-8 *-*

# Should be used on train_nolarge2.graphs 
import sys
from itertools import izip
import re

def make_annotated_corpus(fn1, fn2): 
    print '# IRTG annotated corpus file, v1.0'
    print ''
    print '# interpretation graph: class de.up.ling.irtg.algebra.GraphAlgebra'
    print '# interpretation fourlang: class de.up.ling.irtg.algebra.GraphAlgebra'
    print ''
    with open(sys.argv[1]) as nolarge_graphs, open (sys.argv[2]) as alto_output: 
        for x, y, z in izip(nolarge_graphs, alto_output, alto_output):
            if re.search("^(<null>|null)", y) or  re.search("^(<null>|null)", z):
                continue
            x = x.strip()
            y = y.strip()
            z = z.strip()
            print("{0}\n{1}\n{2}\n{3}".format(x, z, y, ''))

make_annotated_corpus(sys.argv[1], sys.argv[2])
