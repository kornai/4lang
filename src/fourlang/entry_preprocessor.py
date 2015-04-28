from collections import defaultdict
import logging
import re

from unidecode import unidecode

from hunmisc.xstring.encoding import encode_to_proszeky
import nltk.data

assert logging, unidecode  # silence pyflakes

class EntryPreprocessor():
    word_replacement_pairs = [
        (re.compile(patt, re.UNICODE), repl) for patt, repl in [
            (u'/', u'_PER_'), (u'\?', u'_Q_'), (u'\.', u'_P_'),
            (u'\(', u'_LRB_'), (u'\)', u'_RRB_')]]
    def_replacement_pairs = [
        (re.compile(patt, re.UNICODE), repl, flags) for patt, repl, flags in [
            (u'([^,]) etc', u'\\1, etc', ()),  # comma before etc.
            (u'someone or something that is ', u'', ()),
            (u'someone or something that ', u'', ()),
            (u'someone who is ', u'', ('person',)),
            (u'someone who ', u'', ('person',)),
            (u'someone whose job is ', u'', ('person',)),
            (u'^someone ', u'', ('person',)),
            (u'=', u'', ()),
        ]]

    @staticmethod
    def clean_headword(word):
        clean = encode_to_proszeky(word)
        # clean = unidecode(clean)  #will map different words together!
        for pattern, replacement in EntryPreprocessor.word_replacement_pairs:  # nopep8
            clean = pattern.sub(replacement, clean)
        return clean

    def __init__(self, cfg):
        self.cfg = cfg
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.word_counter = defaultdict(int)

    def preprocess_word(self, orig_word, orig_definition=None):
        word = EntryPreprocessor.clean_headword(orig_word)
        return word, set()

    def preprocess_definition(self, orig_definition, word):
        all_flags = set()
        if orig_definition is None:
            return orig_definition, all_flags
        definition = self.sent_detector.tokenize(orig_definition)[0]
        for pattern, replacement, flags in EntryPreprocessor.def_replacement_pairs:  # nopep8
            if pattern.search(definition):
                all_flags |= set(flags)
            definition = pattern.sub(replacement, definition)

        return definition, all_flags

    def preprocess_entry(self, entry):
        if self.cfg.getboolean('filter', 'first_only'):
            entry['senses'] = entry['senses'][:1]
        entry['to_filter'] = self.to_filter(entry['hw'])
        if entry['to_filter']:
            return entry
        entry['hw'], entry['word_flags'] = self.preprocess_word(entry['hw'])
        entry['word_flags'] = sorted(list(entry['word_flags']))
        for sense in entry['senses']:
            sense['definition'], sense['flags'] = self.preprocess_definition(
                sense['definition'], entry['hw'])
            sense['flags'] = sorted(list(sense['flags']))

        return entry

    def to_filter(self, word, definition=None):
        if ' ' in word and not self.cfg.getboolean(
                'filter', 'keep_multiword'):
            return True
        if "'" in word and not self.cfg.getboolean(
                'filter', 'keep_apostrophes'):
            return True
        return False
