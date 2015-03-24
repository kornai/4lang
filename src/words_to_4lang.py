import logging
import os
import sys

from pymachine.wrapper import Wrapper

from utils import ensure_dir

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    out_dir = os.path.join(os.getcwd(), 'data/word_graphs')
    print out_dir
    ensure_dir(out_dir)
    wrapper = Wrapper(sys.argv[1], include_longman=True)
    for line in sys.stdin:
        word = line.strip()
        lemma = wrapper.get_lemma(word, existing_only=True)
        if lemma is None:
            logging.warning("OOV: {0}".format(word))
            continue
        wrapper.draw_single_graph(lemma, out_dir)

if __name__ == "__main__":
    main()
