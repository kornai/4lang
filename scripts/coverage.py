"""Given a dict file and a word frequency list from a corpus, measure type and
token coverage of the dictionary on the corpus"""
import json
import re
import sys

import hunspell

def log(s):
    sys.stderr.write(s+'\n')

lowercase_patt = re.compile('^[a-z]+$')

def discard(word):
    return not bool(lowercase_patt.match(word))

def read_freq(stream):
    counter = {}
    for line in stream:
        freq, word = line.strip().split()
        counter[word] = int(freq)
    return counter

def measure_coverage(defined, counter, hs):
    total_toks, total_types, covered_toks, covered_types = 0, 0, 0, 0
    for word, count in counter.iteritems():
        if discard(word):
            continue
        total_types += 1
        total_toks += count
        if word in defined or any(stem in defined for stem in hs.stem(word)):
            covered_types += 1
            covered_toks += count
        else:
            print "{0}\t{1}".format(count, word)

    log("Coverage:")
    log("{0}/{1} toks ({2:.2f}%)".format(
        covered_toks, total_toks, covered_toks * 100 / float(total_toks)))
    log("{0}/{1} types ({2:.2f}%)".format(
        covered_types, total_types, covered_types * 100 / float(total_types)))

def get_defined(fn, hs):
    defined = set()
    data = json.load(open(fn))
    for word, entry in data.iteritems():
        add_word(word, defined, hs)
        for form in entry.get('alternate_forms', []):
            add_word(form, defined, hs)
    return defined

def add_word(word, defined, hs):
    if discard(word):
        return
    defined.add(word)
    for stem in hs.stem(word):
        defined.add(stem)

def main():
    hs = hunspell.HunSpell(
        '/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff')
    word_freqs = read_freq(open(sys.argv[2]))
    defined = get_defined(sys.argv[1], hs)
    measure_coverage(defined, word_freqs, hs)

if __name__ == '__main__':
    main()
