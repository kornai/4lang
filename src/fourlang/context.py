import cPickle
import logging
import os
import sys

import numpy as np

from dep_to_4lang import DepTo4lang
from dependency_processor import DependencyProcessor
from utils import ensure_dir, get_cfg, get_raw_deps, conll_to_deps


__LOGLEVEL__ = logging.INFO


class Context():
    def __init__(self, cfg):
        self.cfg = cfg
        self.dfl = DepTo4lang(cfg)
        self.dep_processor = DependencyProcessor(cfg)
        self.vocabulary = {"IS_A": 0, "X": 1}
        self.words = ["IS_A", "X"]
        self.binary_vocab = {}
        self.binary_words = []
        self.coocc = [], [], []
        self.zero_array = None
        self.binary_array = None

    @staticmethod
    def load(fn):
        updated_fn = fn + '.pickle' if not fn.endswith('pickle') else fn
        data = cPickle.load(open(updated_fn))
        c = Context(data['cfg'])
        c.words = data['words']
        c.vocabulary = data['vocabulary']
        c.binary_words = data['binary_words']
        c.binary_vocab = data['binary_vocab']
        c.zero_array = data['zero_array']
        c.binary_array = data['binary_array']
        return c

    def save(self):
        fn = self.cfg.get('context', 'context_file')
        updated_fn = fn + '.pickle' if not fn.endswith('pickle') else fn
        data = {
            "words": self.words, "vocabulary": self.vocabulary,
            "binary_words": self.binary_words,
            "binary_vocab": self.binary_vocab, "coocc": self.coocc,
            "zero_array": self.zero_array, "binary_array": self.binary_array,
            "cfg": self.cfg}
        cPickle.dump(data, open(updated_fn, 'w'))

    def freeze_vocab(self):
        self.is_vocab_frozen = True
        self.vocab_size = len(self.vocabulary)
        assert self.vocab_size == len(self.words)
        # 0: IS_A is not listed
        self.binary_size = len(self.binary_vocab)
        assert self.binary_size == len(self.binary_words)

    def ensure_arrays(self):
        if self.zero_array is None:
            logging.info('creating new arrays')
            if not self.is_vocab_frozen:
                logging.warning('freezing vocabulary before creating ndarray')
                self.freeze_vocab()
            self.zero_array = np.zeros(shape=2*(self.vocab_size,), dtype=int)
            self.binary_array = np.zeros(
                shape=(self.binary_size*2, self.vocab_size), dtype=int)
        else:
            logging.info('adding occurences to existing arrays')
        logging.info('# words: {0}'.format(self.vocab_size))
        logging.info('zero_array shape: {0}'.format(self.zero_array.shape))
        logging.info('# binaries: {0}'.format(self.binary_size))
        logging.info('binary_array shape: {0}'.format(self.binary_array.shape))

    def check_edges(self):
        edges, subjs, objs = self.coocc
        edge_no = len(edges)
        assert len(subjs) == edge_no
        assert len(objs) == edge_no

    def build_arrays(self):
        self.ensure_arrays()
        self.check_edges()
        edges, subjs, objs = self.coocc
        for i, edge in enumerate(edges):
            subj, obj = subjs[i], objs[i]
            if edge == 0:
                self.zero_array[subj][obj] += 1
            else:
                binary_word = self.words[edge]
                binary_index = self.binary_vocab[binary_word]
                self.binary_array[2*binary_index][subj] += 1
                self.binary_array[2*binary_index+1][obj] += 1

    def get_w_index(self, word):
        if word in self.vocabulary:
            return self.vocabulary[word]
        else:
            self.words.append(word)
            new_index = len(self.vocabulary)
            self.vocabulary[word] = new_index
            return new_index

    def add_binary(self, word):
        if word in self.binary_vocab:
            return self.binary_vocab[word]
        else:
            self.binary_words.append(word)
            new_index = len(self.binary_vocab)
            self.binary_vocab[word] = new_index
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

            if subj_index or obj_index:
                self.add_binary(word)
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

    def test_activation(self, deps):
        pass


def first_only_filter(sens):
    yield next(sens)
    return


def short_only_filter(sens):
    for deps in sens:
        if len(deps) <= 12:
            yield deps


def test_build(cfg):
    context = Context(cfg)
    # context.build_from_stanford_output(filter_fnc=first_only_filter)
    # context.build_from_stanford_output(filter_fnc=short_only_filter)
    context.build_from_stanford_output()
    context.freeze_vocab()
    context.print_to_files()
    context.build_arrays()  # causes MemoryError
    context.save()

def test_use(cfg):
    fn = cfg.get('context', 'context_file')
    context = Context.load(fn)
    stanford_fn = cfg.get('context', 'stanford_output')
    with open(stanford_fn) as file_obj:
        for deps in conll_to_deps(file_obj):
            context.test_activation(deps)

def main():
    logging.basicConfig(
        level=__LOGLEVEL__,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = get_cfg(cfg_file)

    # test_build(cfg)
    test_use(cfg)

if __name__ == "__main__":
    main()
