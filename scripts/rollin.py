import csv
import sys

fixed_fn = sys.argv[1]
old_fn = sys.argv[2]
new_fn = sys.argv[3]

old_lines = []
with open(old_fn) as old_file:
    csv_reader = csv.reader(old_file, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in csv_reader:
        if len(row) != 9:
            print(row)
            raise ValueError('Length should be 9.')
        old_lines += [row]

fixed_lines = []
with open(fixed_fn) as fixed_file:
    csv_reader = csv.reader(fixed_file, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in csv_reader:
        if len(row) != 9:
            print(row)
            raise ValueError('Length should be 9.')
        fixed_lines += [row]

ids = {}

for line in fixed_lines:
    cur_id = line[4]
    if cur_id in ids:
        raise ValueError(f'{cur_id} is already in use!')
    ids[cur_id] = line

for line in old_lines:
    cur_id = line[4]
    if cur_id not in ids:
        ids[cur_id] = line
        
print(f'Merged dictionary has a size of {len(ids)}.')

with open(new_fn, 'w') as outfile:
    #csv_writer = csv.writer(outfile, delimiter='\t', quoting=csv.QUOTE_NONE)
    for line_num, line in ids.items(): # ids.keys(), ids.values(), ids.items()
        #csv_writer.writerow(line)
        outfile.write("\t".join(line) + "\n")