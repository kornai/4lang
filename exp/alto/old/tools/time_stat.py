import sys

total_time, count = 0, 0
for line in sys.stdin:
    if line.startswith('Processing') or line.startswith('Done'):
        continue
    field1, field2 = line.strip().split()[-2:]
    if field2 == 'ms':
        time = int(field1)
    else:
        if not field2[-1] == 's':
            raise ValueError(line)
        time = 1000*float(field2[:-1])
        if field1[-1] != ']':
            if field1[-1] != 'm':
                raise ValueError(line)
            time += 60000 * int(field1[:-1])

    total_time += time
    count += 1

print ('no. sens: {0}, tot. time: {1}m {2}s, av: {3}'.format(
    count, int(total_time)/60000, (total_time % 60000)/1000.0,
    total_time/float(count)))
