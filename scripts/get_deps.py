import json
import sys

data = json.load(sys.stdin)
for e in data.itervalues():
    if e['hw'] == sys.argv[1]:
        for dep, w1, w2 in e['senses'][0]['definition']['deps']:
            print u"{0}\t{1}\t{2}".format(dep, w1[0], w2[0]).encode("utf-8")

        print e['senses'][0]['definition']['sen'].encode('utf-8')
