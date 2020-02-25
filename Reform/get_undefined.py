import os
import re
from collections import defaultdict

w = defaultdict(int)
concepts = []
with open("1383") as f:
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