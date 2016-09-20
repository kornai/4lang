import cPickle
import logging
import os
import sys

import numpy as np

from dep_to_4lang import DepTo4lang
from dependency_processor import DependencyProcessor
from utils import ensure_dir, get_cfg, get_raw_deps


__LOGLEVEL__ = logging.INFO


class Context():
    def __init__(self, cfg):
        self.cfg = cfg
        self.dfl = DepTo4lang(cfg)
        self.dep_processor = DependencyProcessor(cfg)
        self.vocabulary = {"IS_A": 0, "X": 1}
        self.words = ["X"]
        self.coocc = [], [], []
        self.ndarray = None

    @staticmethod
    def load(cfg):
        pass

    def save(self):
        fn = self.cfg.get('context', 'context_file')
        updated_fn = fn + '.pickle' if not fn.endswith('pickle') else fn
        data = {
            "words": self.words, "vocabulary": self.vocabulary,
            "coocc": self.coocc, "ndarray": self.ndarray, "cfg": self.cfg}
        cPickle.dump(data, open(updated_fn, 'w'))

    def freeze_vocab(self):
        self.is_vocab_frozen = True
        self.vocab_size = len(self.vocabulary)
        assert self.vocab_size == len(self.words) + 1
        # 0: IS_A is not listed

    def check_existing(self):
        if self.ndarray is None:
            if not self.is_vocab_frozen:
                logging.warning('freezing vocabulary before creating ndarray')
                self.freeze_vocab()
            self.ndarray = np.zeros(shape=3*(self.vocab_size,), dtype=int)
        else:
            if not self.ndarray.shape == 3*(self.vocab_size,):
                error_msg = 'ndarray already exists but has shape {0}\
                    instead of {1}'.format(
                        self.ndarray.shape, 3*(self.vocab_size,))
                logging.error(error_msg)
                raise Exception(error_msg)

    def check_edges(self):
        edges, subjs, objs = self.coocc
        edge_no = len(edges)
        assert len(subjs) == edge_no
        assert len(objs) == edge_no

    def build_ndarray(self):
        self.check_existing()
        self.check_edges()
        edges, subjs, objs = self.coocc
        for i, edge in enumerate(edges):
            subj, obj = subjs[i], objs[i]
            self.ndarray[i][subj][obj] += 1

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

    def build_from_stanford_output(self, filter_fnc=lambda x: x):
        dep_file = self.cfg.get('context', 'stanford_output')
        self.build_from_deps(filter_fnc(get_raw_deps(dep_file)))

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

            subj_index, obj_index = None, None
            if machine.partitions[1]:
                subj_index = self.get_w_index(
                    machine.partitions[1][0].printname())
            if machine.partitions[2]:
                obj_index = self.get_w_index(
                    machine.partitions[2][0].printname())

            if subj_index and obj_index:
                self.add_edge(w_index, subj_index, obj_index)
            elif subj_index:
                self.add_edge(w_index, subj_index, 1)
            elif obj_index:
                self.add_edge(w_index, 1, obj_index)
            else:
                pass

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
                f.write(u"{0}\n".format(word).encode('utf-8'))

    def print_edges(self, edge_fn):
        ensure_dir(os.path.dirname(edge_fn))
        logging.info("printing edges to {0}".format(edge_fn))
        with open(edge_fn, 'w') as f:
            for c, i in enumerate(self.coocc[0]):
                j = self.coocc[1][c]
                k = self.coocc[2][c]
                f.write("{0}\t{1}\t{2}\n".format(i, j, k))


def first_only_filter(sens):
    yield next(sens)
    return


def short_only_filter(sens):
    for deps in sens:
        if len(deps) <= 12:
            yield deps


def main():
    logging.basicConfig(
        level=__LOGLEVEL__,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None

    cfg = get_cfg(cfg_file)
    context = Context(cfg)
    # context.build_from_stanford_output(filter_fnc=short_only_filter)
    context.build_from_stanford_output()
    context.freeze_vocab()
    context.build_ndarray()
    context.save()
    context.print_to_files()

if __name__ == "__main__":
    main()
