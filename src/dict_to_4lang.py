from __future__ import with_statement
from ConfigParser import ConfigParser
import json
import logging
import os
import sys
import threading
import time

from stanford_wrapper import StanfordWrapper
from entry_preprocessor import EntryPreprocessor
from longman_parser import LongmanParser
from utils import batches

class DictTo4lang():
    def __init__(self, cfg_file):
        self.cfg_dir = os.path.dirname(cfg_file)
        default_cfg_file = os.path.join(self.cfg_dir, 'default.cfg')
        self.cfg = ConfigParser()
        self.cfg.read([default_cfg_file, cfg_file])
        self.tmp_dir = self.cfg.get('data', 'tmp_dir')
        self.graph_dir = self.cfg.get('data', 'graph_dir')
        self.longman_parser = LongmanParser()
        self.machine_wrapper = None

    def load_machines(self):
        from pymachine.wrapper import Wrapper as MachineWrapper

        machine_cfg_file = os.path.join(self.cfg_dir, 'machine.cfg')
        self.machine_wrapper = MachineWrapper(machine_cfg_file)

    def parse_dict(self):
        input_file = self.cfg.get('data', 'input_file')
        self.dictionary = self.longman_parser.parse_file(input_file)

    def process_entries(self, entries):
        entry_preprocessor = EntryPreprocessor(self.cfg)
        to_parse = []
        for i in range(len(entries)):
            entries[i] = entry_preprocessor.preprocess_entry(entries[i])
            if entries[i]['to_filter']:
                continue
            for sense in entries[i]['senses']:
                sense['definition'] = {"sen": sense['definition'], "deps": []}
                if not sense['definition']['sen'] is None:
                    to_parse.append(sense['definition'])

        stanford_wrapper = StanfordWrapper(self.cfg)
        stanford_wrapper.parse_sentences(to_parse)

        #this is supposed to be thread-safe as long as no two entries have the
        #same headword field, which should be a requirement on the dictionary
        #format, or on the dictionary parser output in the worst case.
        self.word_index.update(
            ((entry['hw'], entry)
                for entry in entries if not entry['to_filter']))

    def process_entries_thread(self, i, entries):
        self.process_entries(entries)
        self.thread_states[i] = True

    def run(self, no_threads=1):
        logging.info('parsing xml...')
        self.parse_dict()
        entries = self.dictionary['entries']
        entries_per_thread = (len(entries) / no_threads) + 1
        self.thread_states = {}
        self.word_index = {}
        # may turn out to be less then "no_threads" with small input
        started_threads = 0
        for i, batch in enumerate(batches(entries, entries_per_thread)):
            t = threading.Thread(
                target=self.process_entries_thread, args=(i, batch))
            t.start()
            started_threads += 1
        logging.info("started {0} threads".format(started_threads))
        while True:
            if len(self.thread_states) < started_threads:
                time.sleep(1)
                continue
            elif all(self.thread_states.values()):
                logging.info(
                    "{0} threads finished successfully".format(no_threads))
            else:
                logging.info("some threads failed")
            break

    def print_4lang_graphs(self):
        for word in self.word_index:
            self.print_4lang_graph(word)

    def print_4lang_graph(self, word):
        from pymachine.utils import MachineGraph
        deps = self.word_index[word]['senses'][0]['definition']['deps']
        machine = self.machine_wrapper.get_dep_definition(word, deps)
        graph = MachineGraph.create_from_machines([machine])
        with open(os.path.join(
                self.graph_dir, u"{0}.dot".format(word)), 'w') as dot_obj:
            dot_obj.write(graph.to_dot().encode('utf-8'))

    def print_dict(self, stream=None):
        if stream is None:
            output_fn = self.cfg.get('data', 'output_file')
            with open(output_fn, 'w') as out:
                json.dump(self.dictionary, out)
        else:
            json.dump(self.dictionary, stream)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1]
    no_threads = int(sys.argv[2])
    dict_to_4lang = DictTo4lang(cfg_file)
    dict_to_4lang.run(no_threads)
    dict_to_4lang.print_dict()
    #dict_to_4lang.load_machines()
    #dict_to_4lang.print_4lang_graphs()
    #dict_to_4lang.print_4lang_graph('aardvark')

if __name__ == '__main__':
    main()
