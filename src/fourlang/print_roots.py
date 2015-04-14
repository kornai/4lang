import json
import re
import sys

dep_regex = re.compile("([a-z_-]*)\((.*?)-([0-9]*)'*, (.*?)-([0-9]*)'*\)")
def main():
    d = json.load(open(sys.argv[1]))
    for word, entry in d.iteritems():
        if entry['to_filter'] or not entry["senses"]:
            continue
        definition = entry["senses"][0]["definition"]
        if definition is None:
            continue
        flags = entry["senses"][0]["flags"]
        sen = definition["sen"]
        for dep in definition["deps"]:
            dep_match = dep_regex.match(dep)
            dep, word1, id1, word2, id2 = dep_match.groups()
            if dep == "root":
                root_word = word2
                break
        print u"{0}\t{1}\t{2}\t{3}".format(
            word, root_word, u",".join(flags), sen).encode("utf-8")

if __name__ == "__main__":
    main()
