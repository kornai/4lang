import getopt
import os
import re
import sys
from collections import defaultdict

concepts_to_left_out = ["HAS", "IN", "=PAT", "AT", "=AGT", "gen", "wh", "PART_OF", "IS_A", "INSTRUMENT", "LACK", "CAUSE",
                        "ER", "MARK", "after", "before", "place", "ON", "other", "FOLLOW", "FROM", "BETWEEN", "FOR", "THROUGH", "NEXT_TO"]


def extract_definition_set(line_id, definitions):
    extracted_definitions = []
    for concept_id in definitions:
        if concept_id != line_id:
            extracted_definitions += definitions[concept_id]

    return set(extracted_definitions)


def main(argv):
    input_file = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "odir="])
    except getopt.GetoptError:
        print('remove_unnecessary.py -i <inputfile> -o <outputdir>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('remove_unnecessary.py -i <inputfile> -o <outputdir>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg

    lines = []
    if not input_file:
        input_file = "/home/adaamko/projects/4lang/Reform/600"
    with open(input_file) as f:
        for line in f:
            lines.append(line.strip("\n"))

    found = True
    while found:
        to_del_index = None
        concepts = []
        line_to_def = defaultdict(list)
        for i, line in enumerate(lines):
            if not line.startswith("%") and len(line.split("\t")) >= 8:
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
                    if not (not wo or wo.startswith("=") or wo.startswith(
                            '"') or wo.isupper() or ">" in wo) and not "<" in wo:
                        w_keys.append(wo.strip())

                line_to_def[i] = w_keys

        for i, line in enumerate(lines):
            if not line.startswith("%") and len(line.split("\t")) >= 8:
                concept = line.split("\t")[0].strip()

                if concept not in concepts_to_left_out:
                    definition_set = extract_definition_set(i, line_to_def)
                    if concept not in definition_set:
                        to_del_index = i
                        break

        if to_del_index:
            #print(lines[to_del_index])
            lines = lines[:to_del_index] + lines[to_del_index+1:]
        else:
            found = False

    if not found:
        for line in lines:
            print(line)


if __name__ == "__main__":
    main(sys.argv[1:])
