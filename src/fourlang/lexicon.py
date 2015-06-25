import cPickle
import logging
import sys

from pymachine.definition_parser import read as read_defs
from pymachine.machine import Machine
from pymachine.control import ConceptControl

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
        definitions = read_defs(file(fn), plural_fn, 0, three_parts=True)
        logging.info('parsed {0} entries, done!'.format(len(definitions)))
        lexicon = Lexicon.create_from_dict(definitions, primitives, cfg)
        return lexicon

    @staticmethod
    def load_from_binary(file_name):
        logging.info('loading lexicon from {0}...'.format(file_name))
        lexicon = cPickle.load(file(file_name))
        logging.info('done!')
        return lexicon

    def save_to_binary(self, file_name):
        logging.info('saving lexicon to {0}...'.format(file_name))
        with open(file_name, 'w') as out_file:
            cPickle.dump(self, out_file)
        logging.info('done!')

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

    def get_words(self):
        return set(self.lexicon.keys()).union(set(self.ext_lexicon.keys()))

    def add(self, printname, machine, external=True):
        if external:
            self._add(printname, machine, self.ext_lexicon)
        else:
            self._add(printname, machine, self.lexicon)

    def _add(self, printname, machine, lexicon):
        if printname in lexicon:
            raise Exception("duplicate word in lexicon: '{0}'".format(lexicon))
        lexicon[printname] = set([machine])

    def get_machine(self, printname):
        machines = self.lexicon.get(
            printname, self.ext_lexicon.get(printname, set()))
        if len(machines) == 0:
            logging.warning(
                'creating new machine for unknown word: "{0}"'.format(
                    printname))
            self.add(printname, Machine(printname, ConceptControl()))
            return self.get_machine(printname)
        else:
            if len(machines) > 1:
                logging.warning('ambiguous printname: {0}'.format(printname))

            return next(iter(machines))

    def expand():
        pass

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = get_cfg(cfg_file)
    lexicon = Lexicon.build_from_4lang(cfg)
    lexicon.save_to_binary(cfg.get("machine", "definitions_binary"))
