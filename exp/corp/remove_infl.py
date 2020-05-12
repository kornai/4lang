import re
import sys

pos_patt = re.compile(r'^\[/([^|\]]*).*')

def remove_infl(pos):
    return pos_patt.sub('\\1', pos)


for line in sys.stdin:
    fields = line.strip().split('\t')
    patt = eval(fields[0])
    new_patt = tuple(remove_infl(pos) for pos in patt)
    rest = "\t".join(fields[1:])
    print(f"{new_patt}\t{rest}")
