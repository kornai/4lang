#!/usr/bin/env python
import sys

from hunmisc.corpustools.tsv_tools import sentence_iterator

from common import sanitize_word


TEMPLATE = ('{0} -> {1}_{0}\n[graph] "({1}<root> / {1})"\n' +
            '[fourlang] "({1}<root> / {1})"\n')


def main():
    seen = set()
    with open(sys.argv[1]) as stream:
        for sentence in sentence_iterator(stream, comment_tag='#'):
            for tok in sentence:
                word = sanitize_word(tok[1])
                pos = tok[3]
                if (word, pos) not in seen:
                    print(TEMPLATE.format(pos, word))
                    seen.add((word, pos))


if __name__ == "__main__":
    main()
