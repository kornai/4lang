from ConfigParser import ConfigParser
import os
import sys

from pymachine.utils import MachineGraph
from pymachine.wrapper import Wrapper as MachineWrapper

from stanford_wrapper import StanfordWrapper

class TextTo4lang():
    def __init__(self, cfg_file):
        self.cfg_dir = os.path.dirname(cfg_file)
        default_cfg_file = os.path.join(self.cfg_dir, 'default.cfg')
        self.cfg = ConfigParser()
        self.cfg.read([default_cfg_file, cfg_file])

    def process(self, stream):
        sens = [line.strip() for line in stream]
        stanford_wrapper = StanfordWrapper(self.cfg)
        parsed_sens = stanford_wrapper.parse_sentences(sens)
        machine_cfg_file = os.path.join(self.cfg_dir, 'machine.cfg')
        machine_wrapper = MachineWrapper(machine_cfg_file)
        for i, sen in enumerate(parsed_sens):
            machine = machine_wrapper.get_dep_definition(
                "sen_{0}".format(i), sen['deps'])
            graph = MachineGraph.create_from_machines([machine])
            f = open('graphs/sens/sen_{0}.dot'.format(i), 'w')
            f.write(graph.to_dot().encode('utf-8'))

if __name__ == "__main__":
    text_to_4lang = TextTo4lang(sys.argv[1])
    text_to_4lang.process(sys.stdin)
