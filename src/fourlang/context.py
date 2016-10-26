from collections import defaultdict
import cPickle
import logging
import os
import sys
import traceback

import numpy as np
import scipy
from scipy.sparse import find

from pymachine.utils import MachineGraph

from dep_to_4lang import DepTo4lang
from dependency_processor import DependencyProcessor
from utils import ensure_dir, get_cfg, get_raw_deps, conll_to_deps, load_sparse_csr, save_sparse_csr  # nopep8


__LOGLEVEL__ = logging.INFO


class Context():
    def __init__(self, cfg):
        self.cfg = cfg
        self.dfl = DepTo4lang(cfg)
        self.dep_processor = DependencyProcessor(cfg)
        self.vocabulary = {}
        self.words = []
        self.binary_vocab = {}
        self.binary_words = []
        self.coocc = [], [], []
        self.zero_array = None
        self.binary_array = None

    @staticmethod
    def load(fn):
        c = Context._load_data(fn)
        c._load_arrays(fn)
        return c

    @staticmethod
    def _load_data(fn):
        updated_fn = fn + '.pickle'
        data = cPickle.load(open(updated_fn))
        c = Context(data['cfg'])
        c.words = data['words']
        c.vocabulary = data['vocabulary']
        c.binary_words = data['binary_words']
        c.binary_vocab = data['binary_vocab']
        return c

    def _load_arrays(self, fn):
        zero_fn = fn + '.npz'
        bin_fn = fn + '.bin.npz'
        self.zero_sparse = load_sparse_csr(zero_fn)
        self.binary_sparse = load_sparse_csr(bin_fn)

    def save(self):
        fn = self.cfg.get('context', 'context_file')
        updated_fn = fn + '.pickle' if not fn.endswith('pickle') else fn
        data = {
            "words": self.words, "vocabulary": self.vocabulary,
            "binary_words": self.binary_words,
            "binary_vocab": self.binary_vocab, "coocc": self.coocc,
            "cfg": self.cfg}
        logging.info('saving cfg, vocabulary, and edges...')
        cPickle.dump(data, open(updated_fn, 'w'))
        logging.info('saving arrays...')
        bin_fn = fn + '.bin'
        save_sparse_csr(fn, self.zero_sparse)
        save_sparse_csr(bin_fn, self.binary_sparse)

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

    def lookup_0_freqs(self, word):
        i = self.vocabulary.get(word)
        if i is None:
            return None
        out_sum = sum(find(self.zero_sparse[i, :])[2])
        in_sum = sum(find(self.zero_sparse[:, i])[2])
        return out_sum, in_sum

    def lookup_arg_freqs(self, word):
        i = self.vocabulary.get(word)
        if i is None:
            return None
        sum1 = sum(find(self.binary_sparse[::2, i])[2])
        sum2 = sum(find(self.binary_sparse[1::2, i])[2])
        return sum1, sum2

    def lookup_bin_freqs(self, word):
        i = self.binary_vocab.get(word)
        if i is None:
            return None
        sum1 = sum(find(self.binary_sparse[2*i, :])[2])
        sum2 = sum(find(self.binary_sparse[2*i+1, :])[2])
        return sum1, sum2

    def lookup_edge(self, edge, subj, obj):
        subj_i, obj_i = map(self.vocabulary.get, (subj, obj))
        if subj_i is None or obj_i is None:
            return None
            # raise Exception("OOV: {0}".format(subj))
        # if obj_i is None:
            # raise Exception("OOV: {0}".format(obj))
        if edge == 'IS_A':
            return self.zero_sparse[subj_i, obj_i]
        else:
            if edge not in self.binary_vocab:
                return None
                # raise Exception("OOV: {0}".format(edge))
            binary_index = self.binary_vocab[edge]
            return (self.binary_sparse[2*binary_index, subj_i],
                    self.binary_sparse[2*binary_index+1, obj_i])

    def build_sparse(self):
        self.check_edges()
        edges, subjs, objs = self.coocc
        values, rows, cols = [], [], []
        bin_values, bin_rows, bin_cols = [], [], []
        for i, edge in enumerate(edges):
            subj, obj = subjs[i], objs[i]
            if edge == 0:
                values.append(1)
                rows.append(subj)
                cols.append(obj)
            else:
                binary_word = self.words[edge]
                binary_index = self.binary_vocab[binary_word]
                bin_values += [1, 1]
                bin_rows += [2*binary_index, 2*binary_index+1]
                bin_cols += [subj, obj]

        self.zero_sparse = scipy.sparse.csr_matrix((values, (rows, cols)))
        self.binary_sparse = scipy.sparse.csr_matrix(
            (bin_values, (bin_rows, bin_cols)))

    def build_array(self):
        self.zero_array = self.zero_sparse.toarray()
        self.binary_array = self.binary_sparse.toarray()
        logging.info('0-array: {0}'.format(self.zero_array.shape))
        logging.info('b-array: {0}'.format(self.binary_array.shape))

    def get_w_index(self, word):
        if word in self.vocabulary:
            return self.vocabulary[word]
        else:
            new_index = len(self.vocabulary)
            self.words.append(word)
            self.vocabulary[word] = new_index
            return new_index

    def add_binary(self, word):
        if word in self.binary_vocab:
            return self.binary_vocab[word]
        else:
            new_index = len(self.binary_vocab)
            self.binary_words.append(word)
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
            # if count % 1000 == 0:
            #    logging.info('processed {0}k sens'.format(count/1000))
            word2machine = self.dfl.get_machines_from_deps_and_corefs(
                [deps], [])
            # self.add_machines(word2machine)
            self.dfl.lexicon.expand(word2machine)
            self.add_edges(word2machine)

    def add_edges(self, word2machine):
        g = MachineGraph.create_from_machines(word2machine.values())
        g.do_closure()
        binaries = defaultdict(lambda: [set(), set()])
        for n1, n2, edata in g.G.edges(data=True):
            n1_index = self.get_w_index(n1.split('_')[0])
            n2_index = self.get_w_index(n2.split('_')[0])
            if edata['color'] == 0:
                self.add_edge(0, n1_index, n2_index)
            else:
                self.add_binary(n1.split('_')[0])
                if edata['color'] == 1:
                    binaries[n1_index][0].add(n2_index)
                elif edata['color'] == 2:
                    binaries[n1_index][1].add(n2_index)
                else:
                    assert False

        for bin_index, (subjs, objs) in binaries.iteritems():
            for subj_index in subjs:
                for obj_index in objs:
                    self.add_edge(bin_index, subj_index, obj_index)

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
        word2machine = self.dfl.get_machines_from_deps_and_corefs([deps], [])
        for word in word2machine:
            if word not in self.vocabulary:
                # print 'OOV:', word
                continue
            i = self.vocabulary[word]
            out_edges = self.zero_array[i, :]
            in_edges = self.zero_array[:, i]
            out_words = dict(
                [(self.words[w], count) for w, count in enumerate(out_edges)
                 if count])
            in_words = dict(
                [(self.words[w], count) for w, count in enumerate(in_edges)
                 if count])
            if out_words:
                top_out = sorted(out_words.items(), key=lambda it: -it[1])[:5]
            if not (out_words or in_words):
                continue
            top_out = sorted(out_words.items(), key=lambda it: -it[1])[:5]
            top_in = sorted(in_words.items(), key=lambda it: -it[1])[:5]
            print 'word: {0}, top_out: {1}, top_in: {2}'.format(
                word, top_out, top_in)


def first_only_filter(sens):
    yield next(sens)
    return


def short_only_filter(sens):
    for deps in sens:
        if len(deps) <= 12:
            yield deps


def test_build_bulk(cfg):
    import gzip
    context = Context(cfg)
    logging.info('building context...')
    path = cfg.get('context', 'stanford_output')
    files = os.listdir(path)
    file_no = len(files)
    sen_count = 0
    for c, fn in enumerate(files):
        logging.info('processing file {0} of {1}'.format(c+1, file_no))
        with gzip.open(os.path.join(path, fn)) as fobj:
            for sen_deps in conll_to_deps(fobj):
                try:
                    context.build_from_deps([sen_deps])
                    sen_count += 1
                    if sen_count % 10000 == 0:
                        logging.info(
                            'processed {0}K sens'.format(sen_count/1000))
                except:
                    logging.warning(
                        'error on sentence {0}: {1}'.format(c, sen_deps))
                    traceback.print_exc()

    context.freeze_vocab()
    logging.info('printing...')
    context.print_to_files()
    logging.info('building arrays...')
    context.build_sparse()
    logging.info('saving context...')
    context.save()
    logging.info('done...')

def test_build(cfg):
    context = Context(cfg)
    # context.build_from_stanford_output(filter_fnc=first_only_filter)
    # context.build_from_stanford_output(filter_fnc=short_only_filter)
    logging.info('building context...')
    context.build_from_stanford_output()
    context.freeze_vocab()
    logging.info('printing...')
    context.print_to_files()
    logging.info('building arrays...')
    context.build_sparse()
    logging.info('saving context...')
    context.save()
    logging.info('done...')

def test_lookup(cfg):
    fn = cfg.get('context', 'context_file')
    logging.info('loading context...')
    context = Context.load(fn)
    logging.info('done...')
    while True:
        print("Type an edge such as 'has man head' or 'IS_A bird vertebrate'")
        x_y_z = raw_input()
        x, y, z = x_y_z.split()
        try:
            print context.lookup_edge(x, y, z)
        except:
            print('error:')
            traceback.print_exc()

def test_spreading(cfg):
    fn = cfg.get('context', 'context_file')
    logging.info('loading context...')
    context = Context.load(fn)
    logging.info('building array...')
    context.build_array()
    logging.info('done...')
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

    # test_build_bulk(cfg)
    # test_build(cfg)
    test_lookup(cfg)
    # test_spreading(cfg)

if __name__ == "__main__":
    main()
