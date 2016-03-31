import copy
import cPickle
import json
import logging
import sys

from nltk.corpus import stopwords as nltk_stopwords
from pymachine.definition_parser import read_defs
from pymachine.machine import Machine
from pymachine.control import ConceptControl
from pymachine.utils import MachineGraph, MachineTraverser

from utils import get_cfg

class Lexicon():
    """A mapping from lemmas to machines"""

    @staticmethod
    def build_from_4lang(cfg):
        fn = cfg.get("machine", "definitions")
        plural_fn = cfg.get("machine", "plurals")
        primitive_fn = cfg.get("machine", "primitives")
        primitives = set(
            [line.decode('utf-8').strip() for line in open(primitive_fn)])
        logging.info('parsing 4lang definitions...')
        pn_index = 1 if cfg.get("deps", "lang") == 'hu' else 0
        definitions = read_defs(
            file(fn), plural_fn, pn_index, three_parts=True)
        logging.info('parsed {0} entries, done!'.format(len(definitions)))
        lexicon = Lexicon.create_from_dict(definitions, primitives, cfg)
        return lexicon

    @staticmethod
    def load_from_binary(file_name):
        logging.info('loading lexicon from {0}...'.format(file_name))
        data = cPickle.load(file(file_name))
        machines_dump, ext_machines_dump = map(
            lambda s: json.loads(data[s]), ("def", "ext"))
        cfg, primitives = data['cfg'], data['prim']
        lexicon = Lexicon.create_from_dumps(machines_dump, ext_machines_dump,
                                            primitives, cfg)
        logging.info('done!')
        return lexicon

    def save_to_binary(self, file_name):
        logging.info('saving lexicon to {0}...'.format(file_name))
        data = {
            "def": json.dumps(Lexicon.dump_machines(self.lexicon)),
            "ext": json.dumps(Lexicon.dump_machines(self.ext_lexicon)),
            "prim": self.primitives,
            "cfg": self.cfg}

        with open(file_name, 'w') as out_file:
            cPickle.dump(data, out_file)
        logging.info('done!')

    @staticmethod
    def create_from_dumps(machines_dump, ext_machines_dump, primitives, cfg):
        """builds the lexicon from dumps created by Lexicon.dump_machines"""
        lexicon = Lexicon(cfg)
        lexicon.primitives = primitives
        for word, dumped_def_graph in machines_dump.iteritems():
            new_machine = Machine(word, ConceptControl())
            lexicon.add_def_graph(word, new_machine, dumped_def_graph)
            lexicon.add(word, new_machine, external=False)

        for word, dumped_def_graph in ext_machines_dump.iteritems():
            new_machine = Machine(word, ConceptControl())
            lexicon.add_def_graph(word, new_machine, dumped_def_graph)
            lexicon.add(word, new_machine, external=True)

        return lexicon

    def add_def_graph(self, word, word_machine, dumped_def_graph,
                      allow_new_base=False, allow_new_ext=False):
        node2machine = {}
        graph = MachineGraph.from_dict(dumped_def_graph)
        for node in graph.nodes_iter():
            pn = "_".join(node.split('_')[:-1])
            if pn == word:
                node2machine[node] = word_machine
            else:
                if not pn:
                    logging.warning(u"empty pn in node: {0}, word: {1}".format(
                        node, word))
                node2machine[node] = self.get_new_machine(pn)

        for node1, adjacency in graph.adjacency_iter():
            machine1 = node2machine[node1]
            for node2, edges in adjacency.iteritems():
                machine2 = node2machine[node2]
                for i, attributes in edges.iteritems():
                    part_index = attributes['color']
                    machine1.append(machine2, part_index)

    @staticmethod
    def dump_definition_graph(machine, seen=set()):
        graph = MachineGraph.create_from_machines([machine])
        return graph.to_dict()

    @staticmethod
    def dump_machines(machines):
        """processes a map of lemmas to machines and dumps them to lists
        of strings, for serialization"""
        dump = {}
        for word, machine_set in machines.iteritems():
            if len(machine_set) > 1:
                raise Exception("cannot dump lexicon with ambiguous \
                    printname: '{0}'".format(word))
            machine = next(iter(machine_set))

            # logging.info('dumping this: {0}'.format(
            #     MachineGraph.create_from_machines([machine]).to_dot()))

            dump[word] = Lexicon.dump_definition_graph(machine)
        return dump

    @staticmethod
    def create_from_dict(word2machine, primitives, cfg):
        lexicon = Lexicon(cfg)
        lexicon.lexicon = dict(word2machine)
        lexicon.primitives = primitives
        return lexicon

    def __init__(self, cfg):
        self.cfg = cfg
        self.lexicon = {}
        self.ext_lexicon = {}
        self.oov_lexicon = {}
        self._known_words = None
        self.expanded = set()
        self.expanded_lexicon = {}
        self.stopwords = set(nltk_stopwords.words('english'))
        self.stopwords.add('as')  # TODO
        self.stopwords.add('root')  # TODO

    def get_words(self):
        return set(self.lexicon.keys()).union(set(self.ext_lexicon.keys()))

    def known_words(self):
        if self._known_words is None:
            self._known_words = self.get_words()
        return self._known_words

    def add(self, printname, machine, external=True, oov=False):
        if printname in self.oov_lexicon:
            assert oov is False
            del self.oov_lexicon[printname]
        lexicon = self.oov_lexicon if oov else (
            self.ext_lexicon if external else self.lexicon)

        self._add(printname, machine, lexicon)

    def _add(self, printname, machine, lexicon):
        if printname in lexicon:
            raise Exception("duplicate word in lexicon: '{0}'".format(lexicon))
        lexicon[printname] = set([machine])

    def get_new_machine(self, printname):
        """returns a new machine without adding it to any lexicon"""
        return Machine(printname, ConceptControl())

    def get_expanded_definition(self, printname):
        machine = self.expanded_lexicon.get(printname)
        if machine is not None:
            return machine

        machine = copy.deepcopy(self.get_machine(printname))
        self.expand_definition(machine)
        self.expanded_lexicon[printname] = machine
        return machine

    def get_machine(self, printname, allow_new_base=False,
                    allow_new_ext=False):
        """returns the lowest level (base < ext < oov) existing machine
        for the printname. If none exist, creates a new machine in the lowest
        level allowed by the allow_* flags. Will always create new machines
        for uppercase printnames"""

        # TODO
        if not printname:
            return self.get_machine("_empty_")

        if printname.isupper():
            return self.get_new_machine(printname)

        machines = self.lexicon.get(
            printname, self.ext_lexicon.get(
                printname, self.oov_lexicon.get(printname, set())))
        if len(machines) == 0:
            # logging.info(
            #    u'creating new machine for unknown word: "{0}"'.format(
            #        printname))
            new_machine = Machine(printname, ConceptControl())
            if allow_new_base:
                self.add(printname, new_machine, external=False)
            elif allow_new_ext:
                self.add(printname, new_machine)
            else:
                self.add(printname, new_machine, oov=True)

            return self.get_machine(printname)
        else:
            if len(machines) > 1:
                debug_str = u'ambiguous printname: {0}, machines: {1}'.format(
                    printname,
                    [lex.get(printname, set([]))
                     for lex in (self.lexicon, self.ext_lexicon,
                                 self.oov_lexicon)])
                raise Exception(debug_str)

            return next(iter(machines))

    def expand_definition(self, machine, stopwords=[]):
        def_machines = dict(
            [(pn, m) for pn, m in [
                (m2.printname(), m2) for m2 in MachineTraverser.get_nodes(
                    machine, names_only=False, keep_upper=True)]
             if pn != machine.printname()])
        self.expand(def_machines, stopwords=stopwords)

    def expand(self, words_to_machines, stopwords=[], cached=False):
        if len(stopwords) == 0:
            stopwords = self.stopwords
        for lemma, machine in words_to_machines.iteritems():
            if (
                    (not cached or lemma not in self.expanded) and
                    lemma in self.known_words() and lemma not in stopwords):

                # deepcopy so that the version in the lexicon keeps its links
                definition = self.get_machine(lemma)
                copied_def = copy.deepcopy(definition)

                """
                for parent, i in list(definition.parents):
                    copied_parent = copy.deepcopy(parent)
                    for m in list(copied_parent.partitions[i]):
                        if m.printname() == lemma:
                            copied_parent.remove(m, i)
                            break
                    else:
                        raise Exception()
                        # "can't find {0} in partition {1} of {2}: {3}".format(
                        # ))
                    copied_parent.append(copied_def, i)
                """

                case_machines = [
                    m for m in MachineTraverser.get_nodes(
                        copied_def, names_only=False, keep_upper=True)
                    if m.printname().startswith('=')]

                machine.unify(copied_def, exclude_0_case=True)

                for cm in case_machines:
                    if cm.printname() == "=AGT":
                        if machine.partitions[1]:
                            machine.partitions[1][0].unify(cm)
                    if cm.printname() == "=PAT":
                        if machine.partitions[2]:
                            machine.partitions[2][0].unify(cm)

                self.expanded.add(lemma)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = get_cfg(cfg_file)
    lexicon = Lexicon.build_from_4lang(cfg)
    lexicon.save_to_binary(cfg.get("machine", "definitions_binary"))
