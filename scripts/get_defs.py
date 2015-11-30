import json
import sys

data = json.load(sys.stdin)
for e in data.itervalues():
    if e['senses'] and e['senses'][0]['definition']:
        print u"{0}\t{1}".format(
            e['hw'], e['senses'][0]['definition']['sen']).encode('utf-8')
