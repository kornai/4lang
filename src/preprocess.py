from collections import defaultdict
from ConfigParser import ConfigParser
import logging
import os
import re
import sys

from hunmisc.xstring.encoding import encode_to_proszeky
import nltk.data

class DictionaryPreprocessor():
    word_replacement_pairs = [(re.compile(patt), repl) for patt, repl in [
        ('/', '_PER_'), ('\?', 'Q'), ('\.', 'P')]]
    def_replacement_pairs = [(re.compile(patt), repl) for patt, repl in [
        ('([^,]) etc', '\1, etc')]]  # comma before etc.

    @staticmethod
    def clean_headword(word):
        clean = encode_to_proszeky(word)
        for pattern, replacement in DictionaryPreprocessor.word_replacement_pairs:  # nopep8
            clean = pattern.sub(replacement, clean)
        return clean

    def __init__(self, cfg_file):
        self.cfg = ConfigParser()
        self.cfg.read(cfg_file)
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.word_counter = defaultdict(int)

    def read_line(self, line):
        try:
            word, definition = line.decode('utf-8').strip().split('\t')
        except:
            logging.warning("couldn't parse line: {0}".format(line))
            word, definition = None, None

        return word, definition

    def preprocess_word(self, orig_word, orig_definition):
        word = DictionaryPreprocessor.clean_headword(orig_word)
        return word

    def preprocess_definition(self, orig_definition, word):
        definition = self.sent_detector.tokenize(orig_definition)[0]
        for pattern, replacement in DictionaryPreprocessor.def_replacement_pairs:  # nopep8
            definition = pattern.sub(replacement, definition)

        return definition

    def preprocess(self, orig_word, orig_definition):
        if self.to_filter(orig_word, orig_definition):
            return None, None
        word = self.preprocess_word(orig_word, orig_definition)
        definition = self.preprocess_definition(orig_definition, word)
        return word, definition

    def to_filter(self, word, definition):
        if ' ' in word and not self.cfg.getboolean(
                'filter', 'keep_multiword'):
            return True
        if "'" in word and not self.cfg.getboolean(
                'filter', 'keep_apostrophes'):
            return True
        return False

    def print_definition(self, word, definition, index, out_dir):
        if index == 0:
            filename = u"{0}.sen".format(word)
        else:
            filename = u"{0}_{1}.sen".format(word, index)

        file_obj = open(os.path.join(out_dir, filename.encode("utf-8")), 'w')
        file_obj.write("{}\n".format(definition.encode("utf-8")))

    def process_all(self):
        input_file = self.cfg.get('data', 'input_file')
        output_dir = self.cfg.get('data', 'output_dir')
        for line in open(input_file):
            raw_word, raw_definition = self.read_line(line)
            if raw_word is None:
                continue
            word, definition = self.preprocess(raw_word, raw_definition)
            if word is None:
                continue
            index = self.word_counter[word]
            if index > 0 and self.cfg.getboolean('filter', 'first_only'):
                continue
            self.print_definition(word, definition, index, output_dir)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1]
    processor = DictionaryPreprocessor(cfg_file)
    processor.process_all()

if __name__ == '__main__':
    main()
