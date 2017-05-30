import json
import sys
import traceback

data = json.load(sys.stdin)
for e in data.itervalues():
    if not e['senses']:
        continue
    defs = [sense.get('definition') for sense in e['senses']]
    for definition in defs:
        if not definition:
            sys.stderr.write(e['hw'].encode('utf-8')+'\n')
            continue
        if isinstance(definition, unicode):
            continue
        print u"{0}\t{1}".format(e['hw'], definition['sen']).encode('utf-8')
