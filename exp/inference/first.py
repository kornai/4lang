import logging
import sys

from pymachine.utils import MachineGraph

from fourlang.corenlp_wrapper import CoreNLPWrapper
# from fourlang.lexicon import Lexicon
from fourlang.dep_to_4lang import DepTo4lang
from fourlang.text_to_4lang import TextTo4lang
from fourlang.utils import get_cfg

__LOGLEVEL__ = "INFO"

class Tester():
    def __init__(self, cfg):
        self.cfg = cfg
        # lex_fn = cfg.get('machine', 'definitions_binary')
        self.dep_to_4lang = DepTo4lang(cfg)
        #                lex = Lexicon.load_from_binary(lex_fn)
        self.parser_wrapper = CoreNLPWrapper(self.cfg)

    def process(self, text):
        preproc = TextTo4lang.preprocess_text(text)
        deps, corefs, parse_trees = self.parser_wrapper.parse_text(preproc)
        machines = self.dep_to_4lang.get_machines_from_deps_and_corefs(
            deps, corefs)
        # print machines
        self.dep_to_4lang.lexicon.expand(machines)
        graph = MachineGraph.create_from_machines(machines.values())
        print graph.to_dot()

def main():
    logging.basicConfig(
        level=__LOGLEVEL__,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = get_cfg(cfg_file)
    tester = Tester(cfg)
    while True:
        text = raw_input('>').strip().decode('utf-8')
        tester.process(text)


if __name__ == "__main__":
    main()
