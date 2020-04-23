import sys

for line in sys.stdin:
    fields = line.strip().split('\t')
    patt = eval(fields[0])
    new_patt = tuple(pos for pos in patt if 'Punct' not in pos)
    rest = "\t".join(fields[1:])
    print(f"{new_patt}\t{rest}")
