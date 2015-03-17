import json
import sys

def print_defs(d):
    for word, entry in d.iteritems():
        if entry['to_filter'] or not entry['senses']:
            continue
        try:
            for sense in entry['senses']:
                if sense['definition'] is None:
                    continue
                print u"{0}\t{1}\t{2}".format(
                    word, sense['pos'], sense['definition']['sen']).encode(
                    "utf-8")
        except:
            print 'error:', sense

def main():
    d = json.load(file(sys.argv[2]))
    if sys.argv[1] == 'defs':
        print_defs(d)


if __name__ == "__main__":
    main()
