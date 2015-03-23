from ConfigParser import ConfigParser
import logging
import os
import sys

from pymachine.utils import MachineGraph
from pymachine.wrapper import Wrapper as MachineWrapper

from corenlp_wrapper import CoreNLPWrapper

__LOGLEVEL__ = 'DEBUG'
__MACHINE_LOGLEVEL__ = 'INFO'

class TextTo4lang():
    def __init__(self, cfg_file):
        self.cfg_dir = os.path.dirname(cfg_file)
        default_cfg_file = os.path.join(self.cfg_dir, 'default.cfg')
        self.cfg = ConfigParser()
        self.cfg.read([default_cfg_file, cfg_file])

    def get_coref_pairs(corefs):
        pass
        #return [[phrase.split()[head_index] for phrase,

    def process(self, stream, max_sens=None):
        sens = [line.strip() for line in stream]

        logging.info("running parser...")
        corenlp_wrapper = CoreNLPWrapper(self.cfg)
        parsed_sens, corefs = corenlp_wrapper.parse_sentences(sens)

        logging.info("loading machine wrapper...")
        logging.getLogger().setLevel(__MACHINE_LOGLEVEL__)
        machine_cfg_file = os.path.join(self.cfg_dir, 'machine.cfg')
        wrapper = MachineWrapper(machine_cfg_file)

        logging.info("processing sentences...")
        for i, deps in enumerate(parsed_sens):
            if max_sens is not None and i >= max_sens:
                break
            with open('test/sens/sen_{0}.dep'.format(i), 'w') as f:
                f.write(
                    "\n".join(["{0}({1}, {2})".format(*dep) for dep in deps]))
        words_to_machines = wrapper.get_machines_from_deps_and_corefs(
            parsed_sens[:max_sens], corefs)
        graph = MachineGraph.create_from_machines(
            words_to_machines.values())
        with open('test/sens/graphs/all_sens.dot'.format(i), 'w') as f:
            f.write(graph.to_dot().encode('utf-8'))
        logging.info("done, processed {0} sentences".format(i+1))

if __name__ == "__main__":
    logging.basicConfig(
        level=__LOGLEVEL__,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    if len(sys.argv) > 1:
        text_to_4lang = TextTo4lang(sys.argv[1])
    else:
        logging.warning('no cfg file specified, using conf/default.cfg')
        text_to_4lang = TextTo4lang('conf/default.cfg')

    max_sens = int(sys.argv[2]) if len(sys.argv) > 2 else None
    text_to_4lang.process(sys.stdin, max_sens)
