import logging
import os
import sys

from corenlp_wrapper import CoreNLPWrapper
from dep_to_4lang import DepTo4lang
from utils import ensure_dir, get_cfg, print_text_graph

__LOGLEVEL__ = 'DEBUG'
__MACHINE_LOGLEVEL__ = 'INFO'

class TextTo4lang():
    def __init__(self, cfg):
        self.cfg = cfg
        self.deps_dir = self.cfg.get('data', 'deps_dir')
        ensure_dir(self.deps_dir)

    def print_deps(self, parsed_sens):
        for i, deps in enumerate(parsed_sens):
            fn = os.path.join(self.deps_dir, 'sen_{0}.dep'.format(i))
            with open(fn, 'w') as f:
                f.write(
                    "\n".join(["{0}({1}, {2})".format(*dep) for dep in deps]))

    def process(self, sens, print_deps=False):
        logging.info("running parser...")
        corenlp_wrapper = CoreNLPWrapper(self.cfg)
        parsed_sens, corefs = corenlp_wrapper.parse_sentences(sens)
        logging.info("parsed {0} sentences".format(len(parsed_sens)))
        if print_deps:
            self.print_deps(parsed_sens)

        logging.info("loading dep_to_4lang...")
        logging.getLogger().setLevel(__MACHINE_LOGLEVEL__)
        dep_to_4lang = DepTo4lang(self.cfg)

        logging.info("processing sentences...")
        words_to_machines = dep_to_4lang.get_machines_from_deps_and_corefs(
            parsed_sens, corefs)

        logging.info("done, processed {0} sentences".format(len(parsed_sens)))

        return words_to_machines

def main():
    logging.basicConfig(
        level=__LOGLEVEL__,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    max_sens = int(sys.argv[2]) if len(sys.argv) > 2 else None

    cfg = get_cfg(cfg_file)
    text_to_4lang = TextTo4lang(cfg)

    input_fn = cfg.get('data', 'input_sens')
    sens = [line.strip() for line in open(input_fn)]
    if max_sens is not None:
        sens = sens[:max_sens]

    words_to_machines = text_to_4lang.process(sens, print_deps=True)
    fn = print_text_graph(words_to_machines, cfg.get('machine', 'graph_dir'))
    logging.info('wrote graph to {0}'.format(fn))

if __name__ == "__main__":
    main()
