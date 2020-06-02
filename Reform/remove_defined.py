import os
import re
import sys, getopt
from collections import defaultdict

def main(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","odir="])
    except getopt.GetoptError:
        print('def_ply_parser.py -i <inputfile> -o <outputdir>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('get_undefined.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg

    w = defaultdict(int)
    concepts = []
    with open(inputfile) as f:
        for line in f:
            if not line.startswith("%"):
                concepts.append(line.split("\t")[0].strip())
                if len(line.split("\t")) > 8:
                    line = line.split("\t")[7].split("%")[0]
                    line = re.sub(",", " ", line)
                    line = re.sub("\{", " ", line)
                    line = re.sub("\}", " ", line)
                    line = re.sub("\(", " ", line)
                    line = re.sub("\)", " ", line)
                    line = re.sub("\[", " ", line)
                    line = re.sub("\]", " ", line)
                    line = re.sub("[0-9]*", "", line)
                    line = re.sub("/", "", line)
                    words = line.split()
                    for wo in words:
                        wo = wo.strip()
                        if wo and not wo.startswith("=") and not wo.startswith('"') and not wo.isupper() and not ">" in wo and not "<" in wo:
                            w[wo.strip()] += 1

    w_keys = w.keys()
    inter = set(concepts) & set(w_keys)
    not_in = {}

    for key in w:
        if key not in inter:
            not_in[key] = w[key]

    t = sorted(not_in.items(), key=lambda x: x[1])

    for elem in t[::-1]:
        print(str(elem[0]) + "\t" + str(elem[1]))


if __name__ == "__main__":
    main(sys.argv[1:])