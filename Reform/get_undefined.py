import os
import re
import sys, getopt
from collections import defaultdict

def main(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:k:d:",["--ifile=","--kfile=","--dfile="])
    except getopt.GetoptError:
        print('get_undefined.py -i <inputfile> -k <keywords> -d <deffile>')
        sys.exit(2)

    inputfile= ""
    keyfile = ""
    dfile = ""
    for opt, arg in opts:
        if opt == '-h':
            print('get_undefined.py -i <inputfile> -k <keywords> -d <deffile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-k", "--kfile"):
            keyfile = arg
        elif opt in ("-d", "--dfile"):
            dfile = arg

    klist = []
    dlist = []
    if keyfile:
        with open(keyfile, "r+") as f:
            for line in f:
                line = line.strip("\n")
                klist.append(line)

    if dfile:
        with open(dfile, "r+") as f:
            for line in f:
                line = line.split("\t")
                keyword = line[0]
                dlist.append(keyword)

    w = defaultdict(int)
    concepts = []
    concept_to_words = defaultdict(list)
    with open(inputfile) as f:
        for line in f:
            if not line.startswith("%"):
                concept = line.split("\t")[0].strip() + "_" + line.split("\t")[4]
                concepts.append(line.split("\t")[0].strip())
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
                    for wo in words:
                        wo = wo.strip()
                        if wo not in dlist and wo not in klist and not ">" in wo and not "<" in wo:
                            concept_to_words[concept].append(wo)
                        if wo and not wo.startswith("=") and not wo.startswith('"') and not wo.isupper() and not ">" in wo and not "<" in wo:
                            w[wo.strip()] += 1

    w_keys = w.keys()
    inter = set(concepts) & set(w_keys)
    not_in = {}

    for key in w:
        if key not in inter:
            not_in[key] = w[key]

    t = sorted(not_in.items(), key=lambda x: x[1])

    sorted_concept_to_words = sorted(concept_to_words.items(), key=lambda x: x[0])

    if not dlist:
        for elem in t[::-1]:
            print(str(elem[0]) + "\t" + str(elem[1]))
    else:
        for elem in sorted_concept_to_words:
            print(elem[0].split("_")[0] + "\t" + " ".join(elem[1]))


if __name__ == "__main__":
    main(sys.argv[1:])
