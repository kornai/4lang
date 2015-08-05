from __future__ import with_statement
from collections import defaultdict
import json
import logging
import os
import sys
import threading
import time
import traceback

from dep_to_4lang import DepTo4lang
from dependency_processor import DependencyProcessor
from entry_preprocessor import EntryPreprocessor
from lexicon import Lexicon
from longman_parser import LongmanParser
from wiktionary_parser import WiktParser
from stanford_wrapper import StanfordWrapper
from utils import batches, ensure_dir, get_cfg

assert Lexicon  # silence pyflakes (Lexicon must be imported for cPickle)

class DictTo4lang():
    def __init__(self, cfg):
        self.dictionary = {}
        self.cfg = cfg
        self.output_fn = self.cfg.get('dict', 'output_file')
        ensure_dir(os.path.dirname(self.output_fn))
        self.tmp_dir = self.cfg.get('data', 'tmp_dir')
        ensure_dir(self.tmp_dir)
        self.graph_dir = self.cfg.get('machine', 'graph_dir')
        ensure_dir(self.graph_dir)
        self.get_parser()
        self.machine_wrapper = None

    def get_parser(self):
        input_type = self.cfg.get('dict', 'input_type')
        logging.info('input type: {0}'.format(input_type))
        if input_type == 'wiktionary':
            self.parser = WiktParser()
        elif input_type == 'longman':
            self.parser = LongmanParser()
        else:
            raise Exception('unknown input format: {0}'.format(input_type))

    def parse_dict(self):
        input_file = self.cfg.get('dict', 'input_file')
        self.raw_dict = defaultdict(dict)
        for entry in self.parser.parse_file(input_file):
            self.unify(self.raw_dict[entry['hw']], entry)

    def unify(self, entry1, entry2):
        if entry1 == {}:
            entry1.update(entry2)
        elif entry1['hw'] != entry2['hw']:
            raise Exception(
                "cannot unify entries with different headwords: " +
                "{0} vs. {1}".format(entry1['hw'], entry2['hw']))

        entry1['senses'] += entry2['senses']

    def process_entries(self, words):
        entry_preprocessor = EntryPreprocessor(self.cfg)
        entries = map(entry_preprocessor.preprocess_entry,
                      (self.raw_dict[word] for word in words))

        stanford_wrapper = StanfordWrapper(self.cfg)
        entries = stanford_wrapper.parse_sentences(
            entries, definitions=True)

        dependency_processor = DependencyProcessor(self.cfg)

        for entry in entries:
            if entry['to_filter']:
                continue
            word = entry['hw']
            for sense in entry['senses']:
                definition = sense['definition']
                if definition is None:
                    continue
                definition['deps'] = dependency_processor.process_dependencies(
                    definition['deps'])

            if word in self.dictionary:
                logging.warning(
                    "entries with identical headwords:\n{0}\n{1}".format(
                        entry, self.dictionary[word]))

                self.unify(self.dictionary[word], entry)
            else:
                self.dictionary[word] = entry

    def process_entries_thread(self, i, words):
        try:
            self.process_entries(words)
        except:
            self.thread_states[i] = False
            traceback.print_exc()
        else:
            self.thread_states[i] = True

    def run(self, no_threads=1):
        logging.info('parsing xml...')
        self.parse_dict()
        entries_per_thread = (len(self.raw_dict) / no_threads) + 1
        self.thread_states = {}
        # may turn out to be less then "no_threads" with small input
        started_threads = 0
        for i, batch in enumerate(batches(self.raw_dict.keys(),
                                  entries_per_thread)):

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
                break
            else:
                raise Exception("some threads failed")

    def print_dict(self, stream=None):
        if stream is None:
            with open(self.output_fn, 'w') as out:
                json.dump(self.dictionary, out)
        else:
            json.dump(self.dictionary, stream)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    no_threads = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    cfg = get_cfg(cfg_file)

    dict_to_4lang = DictTo4lang(cfg)
    dict_to_4lang.run(no_threads)
    dict_to_4lang.print_dict()

    dep_to_4lang = DepTo4lang(cfg)
    dep_to_4lang.dep_to_4lang()
    dep_to_4lang.save_machines()
    dep_to_4lang.print_graphs()


if __name__ == '__main__':
    main()
