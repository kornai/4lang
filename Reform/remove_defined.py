import os
import re
import sys
import getopt
from collections import defaultdict


def main(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "odir="])
    except getopt.GetoptError:
        print('def_ply_parser.py -i <inputfile> -o <outputdir>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('get_undefined.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg

    lines = []
    with open(inputfile) as f:
        for line in f:
            lines.append(line.strip("\n"))

    found = True
    while found:
        to_del_index = None
        concepts = []
        for line in lines:
            if not line.startswith("%"):
                concept = line.split("\t")[0].strip() + \
                    "_" + line.split("\t")[4]
                concepts.append(line.split("\t")[0].strip())

        for i, line in enumerate(lines):
            if not line.startswith("%"):
                if len(line.split("\t")) >= 8:
                    line = line.split("\t")[7].split("%")[0]
                    line = re.sub("@", "", line)
                    line = re.sub('"', "", line)
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
                    w_keys = []
                    for wo in words:
                        wo = wo.strip()
                        if wo and not wo.startswith("=") and not wo.startswith('"') and not wo.isupper() and not ">" in wo and not "<" in wo:
                            w_keys.append(wo.strip())
                    inter = set(concepts) & set(w_keys)
                    if len(inter) == len(set(w_keys)):
                        to_del_index = i
                        break
        if to_del_index:
            lines = lines[:to_del_index] + lines[to_del_index+1:]
        else:
            found = False

    if not found:
        for line in lines:
            print(line)


if __name__ == "__main__":
    main(sys.argv[1:])
