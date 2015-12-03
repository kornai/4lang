import json
import sys

from pymachine.machine import Machine

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
    data = json.load(open(sys.argv[1]))
    if 'deps' in data:
        i = 0 if len(sys.argv) == 3 else int(sys.argv[3])
        sen = data['deps'][i]
        dep_to_dot(sen, sys.argv[2])
    else:
        for word, entry in data.iteritems():
            sen = entry['senses'][0]['definition']['deps']
            fn = "{0}/{1}.dot".format(sys.argv[2], word)
            dep_to_dot(sen, fn)

if __name__ == "__main__":
    main()
