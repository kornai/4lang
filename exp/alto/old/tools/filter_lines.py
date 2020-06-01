#!/usr/bin/env python

import sys
from sets import Set

#Should be used on IRTGs with multiple language preterms/terminals
def filter_lines(fn):
    seen = Set()
    skip = False
    is_empty = True
    file_lines = open(fn, "r").readlines()
    for line in file_lines:
        line = line.strip() 
        if line == "":
            is_empty = True
            skip = False
            print line
            continue
        
        if is_empty == True:
            is_empty = False
            if line in seen:
                skip = True
            else:
                seen.add(line)

        if skip == True:
            continue
        else:
            print line

filter_lines(sys.argv[1])