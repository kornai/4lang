import json
import sys

data = json.load(sys.stdin)
t, d, c = 0, 0, 0
for e in data.itervalues():
    t += 1
    if e['senses'] and e['senses'][0]['definition']:
        d += 1
        if not any(
                dep[0] == 'root' if isinstance(dep, list) else dep.startswith(
                    'root')
                for dep in e['senses'][0]['definition']['deps']):
            c += 1
            if c < 50:
                print u"{0}: {1}".format(
                    e['hw'], e['senses'][0]['definition']['sen'].encode(
                        'utf-8'))

print "entries: {0}, with processed defs: {1}, without root: {2} ({3:.2f}%)".format(  # nopep8
    t, d, c, (c*100)/float(d))
