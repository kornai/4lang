from collections import defaultdict
import cPickle
import json
import logging
import re
import sys
import traceback

from pymachine.control import ConceptControl
from pymachine.lexicon import Lexicon
from pymachine.machine import Machine
from pymachine.operators import AppendOperator, AppendToNewBinaryOperator, AppendToBinaryFromLexiconOperator  # nopep8

from lemmatizer import Lemmatizer
from utils import get_cfg, print_4lang_graphs

class DepTo4lang():

    dep_regex = re.compile("([a-z_-]*)\((.*?)-([0-9]*)'*, (.*?)-([0-9]*)'*\)")

    def __init__(self, cfg):
        self.cfg = cfg
        dep_map_fn = cfg.get("deps", "dep_map")
        self.read_dep_map(dep_map_fn)
        self.lemmatizer = Lemmatizer(cfg)

    def read_dep_map(self, dep_map_fn):
        self.dependencies = {}
        for line in file(dep_map_fn):
            l = line.strip()
            if not l or l.startswith('#'):
                continue
            dep = Dependency.create_from_line(l)
            self.dependencies[dep.name] = dep

    def apply_dep(self, dep_str, machine1, machine2, lexicon=None):
        self.dependencies[dep_str].apply(machine1, machine2, lexicon)

    def dep_to_4lang(self):
        dict_fn = self.cfg.get("dict", "output_file")
        logging.info('reading dependencies from {0}...'.format(dict_fn))
        longman = json.load(open(dict_fn))
        self.words_to_machines = {}
        for c, (word, entry) in enumerate(longman.iteritems()):
            if c % 1000 == 0:
                logging.info("added {0}...".format(c))
            try:
                if entry["to_filter"]:
                    continue
                if not entry['senses']:
                    #  TODO these are words that only have pointers to an MWE
                    #  that they are part of.
                    continue
                definition = entry['senses'][0]['definition']
                if definition is None:
                    continue
                deps = definition['deps']
                if not deps:
                    #  TODO see previous comment
                    continue
                machine = self.get_dep_definition(word, deps)
                if machine is None:
                    continue
                self.words_to_machines[word] = machine
            except Exception:
                logging.error(
                    u'skipping "{0}" because of an exception:'.format(
                        word))
                logging.info("entry: {0}".format(entry))
                traceback.print_exc()
                continue

        logging.info('done!')

    def print_graphs(self):
        print_4lang_graphs(
            self.words_to_machines,
            self.cfg.get('machine', 'graph_dir'))

    def save_machines(self):
        out_fn = self.cfg.get("machine", "ext_definitions")
        logging.info('saving machines to {0}...'.format(out_fn))
        with open(out_fn, 'w') as out_file:
            cPickle.dump(self.words_to_machines, out_file)
        logging.info('done!')

    @staticmethod
    def parse_dependency(string):
        dep_match = DepTo4lang.dep_regex.match(string)
        if not dep_match:
            raise Exception('cannot parse dependency: {0}'.format(string))
        dep, word1, id1, word2, id2 = dep_match.groups()
        return dep, (word1, id1), (word2, id2)

    def get_dep_definition(self, word, deps):
        root_deps = filter(lambda d: d[0] == 'root', deps)
        if len(root_deps) != 1:
            logging.warning(
                'no unique root dependency, skipping word "{0}"'.format(word))
            return None
        root_word, root_id = root_deps[0][2]
        root_lemma = self.lemmatizer.lemmatize(root_word).replace('/', '_PER_')
        word2machine = self.get_machines_from_parsed_deps(deps)

        root_machine = word2machine[root_lemma]
        word_machine = word2machine.get(word, Machine(word, ConceptControl()))
        word_machine.append(root_machine, 0)
        return word_machine

    def get_machines_from_deps(self, dep_strings):
        # deprecated, use get_machines_from_deps_and_corefs
        deps = map(DepTo4lang.parse_dependency, dep_strings)
        return self.get_machines_from_parsed_deps(deps)

    def get_machines_from_parsed_deps(self, deps):
        # deprecated, use get_machines_from_deps_and_corefs
        return self.get_machines_from_deps_and_corefs([deps], [])

    def get_machines_from_deps_and_corefs(self, dep_lists, corefs):
        coref_index = defaultdict(dict)
        for (word, sen_no), mentions in corefs:
            for m_word, m_sen_no in mentions:
                coref_index[m_word][m_sen_no-1] = word

        # logging.info('coref index: {0}'.format(coref_index))

        lexicon = Lexicon()
        word2machine = {}

        for i, deps in enumerate(dep_lists):
            for dep, (word1, id1), (word2, id2) in deps:
                # logging.info('w1: {0}, w2: {1}'.format(word1, word2))
                c_word1 = coref_index[word1].get(i, word1)
                c_word2 = coref_index[word2].get(i, word2)
                if c_word1 != word1:
                    logging.warning(
                        "unifying '{0}' with canonical '{1}'".format(
                            word1, c_word1))
                if c_word2 != word2:
                    logging.warning(
                        "unifying '{0}' with canonical '{1}'".format(
                            word2, c_word2))

                # logging.info('cw1: {0}, cw2: {1}'.format(c_word1, c_word2))
                lemma1 = self.lemmatizer.lemmatize(c_word1)
                lemma2 = self.lemmatizer.lemmatize(c_word2)

                lemma1 = c_word1 if lemma1 is None else lemma1
                lemma2 = c_word2 if lemma2 is None else lemma2

                # TODO
                lemma1 = lemma1.replace('/', '_PER_')
                lemma2 = lemma2.replace('/', '_PER_')

                # logging.info(
                #     'lemma1: {0}, lemma2: {1}'.format(lemma1, lemma2))
                machine1, machine2 = self._add_dependency(
                    dep, (lemma1, id1), (lemma2, id2), lexicon)

                word2machine[lemma1] = machine1
                word2machine[lemma2] = machine2

        return word2machine

    def add_dependency(self, string):
        # e.g. nsubjpass(pushed-7, salesman-5)
        logging.debug('processing dependency: {}'.format(string))
        dep, (word1, id1), (word2, id2) = DepTo4lang.parse_dependency(string)
        lemma1 = self.lemmatizer.lemmatize(word1)
        lemma2 = self.lemmatizer.lemmatize(word2)
        self._add_dependency(dep, (lemma1, id1), (lemma2, id2),
                             use_lexicon=True, activate_machines=True)

    def _add_dependency(self, dep, (word1, id1), (word2, id2), lexicon):
        """Given a triplet from Stanford Dep.: D(w1,w2), we create and activate
        machines for w1 and w2, then run all operators associated with D on the
        sequence of the new machines (m1, m2)"""
        # logging.info(
        #     'adding dependency {0}({1}, {2})'.format(dep, word1, word2))
        machine1, machine2 = map(lexicon.get_machine, (word1, word2))

        self.apply_dep(dep, machine1, machine2, lexicon)
        return machine1, machine2


class Dependency():
    def __init__(self, name, operators=[]):
        self.name = name
        self.operators = operators

    @staticmethod
    def create_from_line(line):
        rel, reverse = None, False
        logging.debug('parsing line: {}'.format(line))
        fields = line.split('\t')
        if len(fields) == 2:
            dep, edges = fields
        elif len(fields) == 3:
            dep, edges, rel = fields
            if rel[0] == '!':
                rel = rel[1:]
                reverse = True
        else:
            raise Exception('lines must have 2 or 3 fields: {}'.format(
                fields))

        edge1, edge2 = map(lambda s: int(s) if s not in ('-', '?') else None,
                           edges.split(','))

        if dep.startswith('prep_') and rel is None:
            rel = dep.split('_', 1)[1].upper()

        return Dependency(dep, Dependency.get_standard_operators(
            edge1, edge2, rel, reverse))

    @staticmethod
    def get_standard_operators(edge1, edge2, rel, reverse):
        operators = []
        if edge1 is not None:  # it can be zero, don't check for truth value!
            operators.append(AppendOperator(0, 1, part=edge1))
        if edge2 is not None:
            operators.append(AppendOperator(1, 0, part=edge2))
        if rel:
            operators.append(
                AppendToNewBinaryOperator(rel, 0, 1, reverse=reverse))
            # operators.append(
            #    AppendToBinaryFromLexiconOperator(rel, 0, 1, reverse=reverse))

        return operators

    def apply(self, machine1, machine2, lexicon=None):
        for operator in self.operators:
            if isinstance(operator, AppendToBinaryFromLexiconOperator):
                operator.act((machine1, machine2), lexicon)
            else:
                operator.act((machine1, machine2))

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = get_cfg(cfg_file)
    dep_to_4lang = DepTo4lang(cfg)
    dep_to_4lang.dep_to_4lang()
    dep_to_4lang.save_machines()
    dep_to_4lang.print_graphs()

if __name__ == "__main__":
    main()
