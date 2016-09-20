import logging
import os
import sys

from dep_to_4lang import DepTo4lang
from dependency_processor import DependencyProcessor
from utils import ensure_dir, get_cfg, get_raw_deps


__LOGLEVEL__ = logging.INFO


class Context():
    def __init__(self, cfg):
        self.cfg = cfg
        self.dfl = DepTo4lang(cfg)
        self.dep_processor = DependencyProcessor(cfg)
        self.vocabulary = {"IS_A": 0}
        self.words = ["IS_A"]
        self.coocc = [], [], []

    def get_w_index(self, word):
        if word in self.vocabulary:
            return self.vocabulary[word]
        else:
            self.words.append(word)
            new_index = len(self.vocabulary)
            self.vocabulary[word] = new_index
            return new_index

    def add_edge(self, w0_index, w1_index, w2_index):
        self.coocc[0].append(w0_index)
        self.coocc[1].append(w1_index)
        self.coocc[2].append(w2_index)

    def build_from_stanford_output(self):
        dep_file = self.cfg.get('context', 'stanford_output')
        self.build_from_deps(get_raw_deps(dep_file))

    def build_from_deps(self, sen_deps):
        count = 0
        for deps in sen_deps:
            count += 1
            if count % 1000 == 0:
                logging.info('processed {0}k sens'.format(count/1000))
            word2machine = self.dfl.get_machines_from_deps_and_corefs(
                [deps], [])
            self.add_machines(word2machine)

    def add_machines(self, word2machine):
        for word, machine in word2machine.iteritems():
            w_index = self.get_w_index(word)
            for child in machine.partitions[0]:
                c_index = self.get_w_index(child.printname())
                self.add_edge(0, w_index, c_index)

    def print_to_files(self):
        ensure_dir
        fn = self.cfg.get('context', 'raw_output')
        vocab_fn = "{0}.vocab".format(fn)
        self.print_vocab(vocab_fn)
        edge_fn = "{0}.edges".format(fn)
        self.print_edges(edge_fn)

    def print_vocab(self, vocab_fn):
        ensure_dir(os.path.dirname(vocab_fn))
        logging.info("printing vocabulary to {0}".format(vocab_fn))
        with open(vocab_fn, 'w') as f:
            for word in self.words:
                f.write("{0}\n".format(word))

    def print_edges(self, edge_fn):
        ensure_dir(os.path.dirname(edge_fn))
        logging.info("printing edges to {0}".format(edge_fn))
        with open(edge_fn, 'w') as f:
            for c, i in enumerate(self.coocc[0]):
                j = self.coocc[1][c]
                k = self.coocc[2][c]
                f.write("{0}\t{1}\t{2}\n".format(i, j, k))


def main():
    logging.basicConfig(
        level=__LOGLEVEL__,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None

    cfg = get_cfg(cfg_file)
    context = Context(cfg)
    context.build_from_stanford_output()
    context.print_to_files()

if __name__ == "__main__":
    main()
