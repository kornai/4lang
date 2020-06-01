"""process CONLL-formatted dependencies and output our internal format"""
import logging
import sys

from hunmisc.corpustools.tsv_tools import sentence_iterator, get_dependencies


def main():
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")

    id_field, word_field, lemma_field, msd_field, gov_field, dep_field = (
            0, 1, None, None, -4, -3)

    with open(sys.argv[1]) as stream:
        c = 0
        for sentence in sentence_iterator(stream, comment_tag='#'):
            try:
                deps = get_dependencies(
                    sentence, id_field, word_field, lemma_field, msd_field,
                    gov_field, dep_field)
            except:
                print(sentence)
                sys.exit(-1)
            print(deps)
            sys.exit(-1)
            c += 1
            if c % 1000 == 0:
                print(c)
        print(c)

if __name__ == "__main__":
    main()
