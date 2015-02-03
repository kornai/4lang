from collections import defaultdict
import logging
import os
import sys

from hunmisc.xstring.encoding import encode_to_proszeky
import nltk.data

replacement_pairs = [('/', '_PER_'), ('?', 'Q'), ('.', 'P')]

def clean_headword(word):
    clean = encode_to_proszeky(word)
    for a, b in replacement_pairs:
        clean = clean.replace(a, b)
    return clean

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    out_dir = sys.argv[1]
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    word_counter = defaultdict(int)
    for line in sys.stdin:
        try:
            word, definition = line.decode('utf-8').strip().split('\t')
        except:
            logging.warning("couldn't parse line: {0}".format(line))
            continue
        if ' ' in word or "'" in word:
            continue
        clean_word = clean_headword(word)
        try:
            if clean_word not in word_counter:
                filename = "{0}.sen".format(clean_word)
            else:
                filename = "{0}_{1}.sen".format(clean_word,
                                                word_counter[clean_word])
        except UnicodeEncodeError:
            continue

        word_counter[clean_word] += 1
        out_file = os.path.join(out_dir, filename)
        f_obj = open(out_file, 'w')
        sen = sent_detector.tokenize(definition)[0]
        f_obj.write("{}\n".format(sen.encode('utf-8')))

if __name__ == '__main__':
    main()
