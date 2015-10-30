import json
import sys

data = json.load(sys.stdin)
cc, c, t = 0, 0, 0
for e in data.itervalues():
    cc += 1
    if e['senses'] and e['senses'][0]['definition'] and not e['to_filter']:
        c += 1
        t += len(e['senses'][0]['definition']['sen'].split())

print "{0} words in {1} definitions ({2} entries), average: {3:.2f}".format(
    t, c, cc, t/float(c))
