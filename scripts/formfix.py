import csv
import sys
import re

old_fn = sys.argv[1]
new_fn = sys.argv[2]


class DicLine:
    def __init__(self, en, hu, la, pl, key, status="u", pos="N", definition="TODO", comment="%"):
        self.en = en
        self.hu = hu
        self.la = la
        self.pl = pl
        self.key = key
        self.status = status
        self.pos = pos
        self.definition = definition
        if comment == "" or not re.match(r'%', comment):
            self.comment = "%" + comment
        else:
            self.comment = comment

    def __str__(self):
        return '\t'.join([self.en, self.hu, self.la, self.pl, self.key, self.status, self.pos, self.definition, self.comment])


old_lines = {}
with open(old_fn) as old_file:
    csv_reader = csv.reader(old_file, delimiter='\t')
    for row in csv_reader:
        curline = DicLine(*row[:9])
        if curline.key in old_lines:
            raise ValueError(f'{curline.key} is already in use!')
        old_lines[curline.key] = curline


def syntax_error(entry):
    return (
        not re.match(r'^(\w|[#-])*$', entry.en) or
        not re.match(r'^(\w|[#-])*$', entry.pl) or
        not re.match(r'^(\w|[#-])*$', entry.la) or
        not re.match(r'^(\w|[#-])*$', entry.hu) or
        not entry.key.isnumeric() or
        not entry.status in {"u", "c", "p", "e"} or
        not entry.pos in {"N", "A", "G", "U", "V", "D"} or
        entry.definition == "" or
        not re.match(r'%', entry.comment)
    )


for line_num, line in old_lines.items():
    if syntax_error(line):
        print(str(line))  # python magic method __XX__

with open(new_fn, 'w') as outfile:
    for entry_id in old_lines:
        print(str(old_lines[entry_id]), file=outfile)
