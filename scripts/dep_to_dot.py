import json
import sys

from pymachine.machine import Machine
from fourlang.dependency_processor import Dependencies

HEADER = u"digraph finite_state_machine {\n\tdpi=100;\n\trankdir=LR;\n"
EXCLUDE = ("punct")

def dep_to_dot(deps, fn):
    try:
        edges = [
            (d['dep']['lemma'], d['type'], d['gov']['lemma']) for d in deps
            if d['type'] not in EXCLUDE]
    except:
        edges = [(d[1][0], d[0], d[2][0]) for d in deps if d[0] not in EXCLUDE]
    words = set([e[0] for e in edges] + [e[2] for e in edges])
    lines = []
    for word in words:
        lines.append(u'\t{0} [shape=rectangle, label="{0}"];'.format(
            Machine.d_clean(word)))
    for edge in edges:
        dep, dtype, gov = map(Machine.d_clean, edge)
        lines.append(u'\t{0} -> {1} [label="{2}"];'.format(dep, gov, dtype))
    with open(fn, 'w') as f:
        f.write(HEADER.encode("utf-8"))
        f.write(u"\n".join(lines).encode("utf-8"))
        f.write("}\n")

def main():
    if sys.argv[1] == '-':
        # USAGE 1: read raw stanford output from stdin
        dep_to_dot(map(
            lambda l: Dependencies.parse_dependency(l.strip()),
            sys.stdin.readlines()), sys.argv[2])
    else:
        data = json.load(open(sys.argv[1]))
        try:
            # USAGE 2: choose a sentence by number from text_to_4lang output
            i = int(sys.argv[3])
        except:
            # USAGE 3: pick a word from JSON
            # dep_to_dot.py input_json output_dir word
            w = sys.argv[3]
            deps = data[w]['senses'][0]['definition']['deps']
            try:
                sen = map(Dependencies.parse_dependency, deps)
            except:
                sen = deps
            fn = u"{0}/{1}.dot".format(sys.argv[2], w).encode('utf-8')
            dep_to_dot(sen, fn)
        else:
            sen = data['deps'][i]
            dep_to_dot(sen, sys.argv[2])

if __name__ == "__main__":
    main()
