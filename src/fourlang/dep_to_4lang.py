from collections import defaultdict
import json
import logging
import os
import re
import sys
import traceback

from pymachine.operators import AppendOperator, AppendToNewBinaryOperator, AppendToBinaryFromLexiconOperator  # nopep8

from dependency_processor import DependencyProcessor, Dependencies, NewDependencies  # nopep8
from lemmatizer import Lemmatizer
from lexicon import Lexicon
from utils import ensure_dir, get_cfg, print_4lang_graphs


class DepTo4lang():

    dep_regex = re.compile("([a-z_-]*)\((.*?)-([0-9]*)'*, (.*?)-([0-9]*)'*\)")

    def __init__(self, cfg, direct_parse=False):
        self.cfg = cfg
        self.lang = self.cfg.get("deps", "lang")
        if(not direct_parse):
            self.out_fn = self.cfg.get("machine", "definitions_binary_out")
            ensure_dir(os.path.dirname(self.out_fn))
        self.dependency_processor = DependencyProcessor(self.cfg)
        dep_map_fn = cfg.get("deps", "dep_map")
        self.read_dep_map(dep_map_fn)
        self.undefined = set()
        self.lemmatizer = Lemmatizer(cfg)
        self.lexicon_fn = self.cfg.get("machine", "definitions_binary")
        self.lexicon = Lexicon.load_from_binary(self.lexicon_fn)
        self.word2lemma = {}
        self.first_only = cfg.getboolean('filter', 'first_only')

    def read_dep_map(self, dep_map_fn):
        self.dependencies = defaultdict(list)
        for line in file(dep_map_fn):
            l = line.strip()
            if not l or l.startswith('#'):
                continue
            dep = Dependency.create_from_line(l)
            self.dependencies[dep.name].append(dep)

    def apply_dep(self, dep, machine1, machine2):
        dep_type = dep['type']
        msd1 = dep['gov'].get('msd')
        msd2 = dep['dep'].get('msd')
        if dep_type not in self.dependencies:
            if dep_type not in self.undefined:
                self.undefined.add(dep_type)
                logging.warning(
                    'skipping dependency not in dep_to_4lang map: {0}'.format(
                        dep_type))
            return False  # not that anyone cares
        for dep in self.dependencies[dep_type]:
            dep.apply(msd1, msd2, machine1, machine2)

    def dep_to_4lang(self):
        dict_fn = self.cfg.get("dict", "output_file")
        logging.info('reading dependencies from {0}...'.format(dict_fn))
        longman = json.load(open(dict_fn))
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

                unified_machine = None

                for sense in entry['senses']:
                    if sense['mwe'] is not None:
                        continue
                    definition = sense['definition']
                    if definition is None:
                        continue
                    deps = definition['deps']
                    if not deps:
                        #  TODO see previous comment
                        continue
                    machine = self.get_dep_definition(word, deps)
                    if machine is None:
                        continue
                    if unified_machine is None:
                        unified_machine = machine
                    else:
                        unified_machine.unify(machine)
                    if self.first_only == True:
                        break
                self.lexicon.add(word, unified_machine)
            except Exception:
                logging.error(u"exception caused by: '{0}'".format(word))
                # logging.error(
                #     u'skipping "{0}" because of an exception:'.format(
                #         word))
                # logging.info("entry: {0}".format(entry))
                traceback.print_exc()
                sys.exit(-1)
                continue

        logging.info('added {0}, done!'.format(c + 1))

    def print_graphs(self):
        print_4lang_graphs(
            self.lexicon.ext_lexicon,
            self.cfg.get('machine', 'graph_dir'))

    def save_machines(self):
        self.lexicon.save_to_binary(self.out_fn)

    @staticmethod
    def parse_dependency(string):
        dep_match = DepTo4lang.dep_regex.match(string)
        if not dep_match:
            raise Exception('cannot parse dependency: {0}'.format(string))
        dep, word1, id1, word2, id2 = dep_match.groups()
        return dep, (word1, id1), (word2, id2)

    def get_root_lemmas(self, deps):
        return [
            d['dep'].setdefault(
                'lemma', self.lemmatizer.lemmatize(
                    d['dep']['word'], uppercase=True))
            for d in deps if d['type'] == 'root']  # TODO

    def get_dep_definition(self, word, deps):
        if isinstance(deps[0], unicode):
            # TODO
            root_lemmas = self.get_root_lemmas(
                NewDependencies.create_from_old_deps(
                    Dependencies.create_from_strings(deps)).deps)
        else:
            root_lemmas = self.get_root_lemmas(deps)
        deps = self.dependency_processor.process_dependencies(deps)
        if not root_lemmas:
            logging.warning(
                u'no root dependency, skipping word "{0}"'.format(word))
            return None

        word2machine = self.get_machines_from_deps_and_corefs(
            [deps], [], process_deps=False)

        if word in word2machine:
            return word2machine[word]

        root_machines = filter(None, map(word2machine.get, root_lemmas))
        if not root_machines:
            logging.info("failed to find root machine")
            logging.info('root lemmas: {0}'.format(root_lemmas))
            logging.info('word2machine: {0}'.format(word2machine))
            logging.info('word: {0}'.format(word))
            sys.exit(-1)

        word_machine = self.lexicon.get_machine(word, new_machine=True)

        for root_machine in root_machines:
            word_machine.unify(root_machine)
            word_machine.append(root_machine, 0)
        return word_machine

    def get_machines_from_deps_and_corefs(
            self, dep_lists, corefs, process_deps=True):
        if process_deps:
            dep_lists = map(
                self.dependency_processor.process_dependencies, dep_lists)
        coref_index = defaultdict(dict)
        for (word, sen_no), mentions in corefs:
            for m_word, m_sen_no in mentions:
                coref_index[m_word][m_sen_no-1] = word

        # logging.info('coref index: {0}'.format(coref_index))

        word2machine = {}
        for deps in dep_lists:
            for dep in deps:
                for t in (dep['gov'], dep['dep']):
                    self.word2lemma[t['word']] = t.setdefault(
                        'lemma', self.lemmatizer.lemmatize(
                            t['word'], uppercase=True))

        for i, deps in enumerate(dep_lists):
            try:
                for dep in deps:
                    word1 = dep['gov']['word']
                    word2 = dep['dep']['word']
                    # logging.info('dep: {0}, w1: {1}, w2: {2}'.format(
                    #     repr(dep), repr(word1), repr(word2)))
                    c_word1 = coref_index[word1].get(i, word1)
                    c_word2 = coref_index[word2].get(i, word2)

                    """
                    if c_word1 != word1:
                        logging.warning(
                            "unifying '{0}' with canonical '{1}'".format(
                                word1, c_word1))
                    if c_word2 != word2:
                        logging.warning(
                            "unifying '{0}' with canonical '{1}'".format(
                                word2, c_word2))
                    """
                    lemma1 = self.word2lemma[c_word1]
                    lemma2 = self.word2lemma[c_word2]

                    # TODO
                    # lemma1 = lemma1.replace('/', '_PER_')
                    # lemma2 = lemma2.replace('/', '_PER_')

                    # logging.info(
                    #     'lemma1: {0}, lemma2: {1}'.format(
                    #         repr(lemma1), repr(lemma2)))

                    for lemma in (lemma1, lemma2):
                        if lemma not in word2machine:
                            word2machine[lemma] = self.lexicon.get_machine(
                                lemma, new_machine=True)

                    self.apply_dep(
                        dep, word2machine[lemma1], word2machine[lemma2])

            except:
                logging.error(u"failure on dep: {0}({1}, {2})".format(
                    dep, word1, word2))
                traceback.print_exc()
                raise Exception("adding dependencies failed")

        return word2machine


class Dependency():
    def __init__(self, name, patt1, patt2, operators=[]):
        self.name = name
        self.patt1 = re.compile(patt1) if patt1 else None
        self.patt2 = re.compile(patt2) if patt2 else None
        self.operators = operators

    @staticmethod
    def create_from_line(line):
        rel, reverse = None, False
        # logging.debug('parsing line: {}'.format(line))
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

        if ',' in dep:
            dep, patt1, patt2 = dep.split(',')
        else:
            patt1, patt2 = None, None

        edge1, edge2 = map(lambda s: int(s) if s not in ('-', '?') else None,
                           edges.split(','))

        if (dep.startswith('prep_') or
                dep.startswith('prepc_')) and rel is None:
            # logging.info('adding new rel from: {0}'.format(dep))
            rel = dep.split('_', 1)[1].upper()

        # Universal Dependencies
        if ((dep.startswith('acl:') and not dep.startswith('acl:relcl')) or
                dep.startswith('advcl:') or
                dep.startswith('nmod:')) and rel is None:
            logging.info('adding new rel from: {0}'.format(dep))
            rel = dep.split(':', 1)[1].upper()

        return Dependency(dep, patt1, patt2, Dependency.get_standard_operators(
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

        return operators

    def match(self, msd1, msd2):
        for patt, msd in ((self.patt1, msd1), (self.patt2, msd2)):
            if patt is not None and msd is not None and not patt.match(msd):
                return False
        return True

    def apply(self, msd1, msd2, machine1, machine2):
        logging.debug(
            'trying {0} on {1} and {2}...'.format(self.name, msd1, msd2))
        if self.match(msd1, msd2):
            logging.debug('MATCH!')
            for operator in self.operators:
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
