import logging
import os
import sys

from hunmisc.utils.huntool_wrapper import Hundisambig, Ocamorph, OcamorphAnalyzer, MorphAnalyzer  # nopep8
from stemming.porter2 import stem as porter_stem

from utils import get_cfg

class Lemmatizer():

    def __init__(self, cfg):
        self.cfg = cfg
        self.analyzer, self.morph_analyzer = self.get_analyzer()

        self.read_cache()
        self.oov = set()

    def clear_cache(self):
        self.cache = {}
        self.oov = set()

    def _analyze(self, word):
        stem = porter_stem(word)
        lemma = list(self.analyzer.analyze(
            [[word]]))[0][0][1].split('||')[0].split('<')[0]

        cand_krs = self.morph_analyzer.analyze([[word]]).next().next()
        candidates = [cand.split('||')[0].split('<')[0] for cand in cand_krs]

        self.cache[word] = (stem, lemma, candidates)

    def lemmatize(self, word, defined=None, stem_first=False,
                  debug=False):
        # if 'defined' is provided, will refuse to return lemmas not in it

        # if the word is defined, we just return it
        if defined is not None and word in defined:
            return word

        # if the word is not in our cache, we run all analyses
        if word not in self.cache:
            self._analyze(word)

        stem, lemma, candidates = self.cache[word]

        # if stem_first flag is on, we rerun lemmatize on the stem
        # and return the result unless it doesn't exist
        if stem_first:
            if defined is None:
                logging.warning("stem_first=True and defined=None, \
                                'lemmatize' is now a blind Porter stemmer")
            stemmed_lemma = self.lemmatize(
                stem, defined=defined, stem_first=False)
            if stemmed_lemma is not None:
                return stemmed_lemma

        # we return the lemma unless it's not in defined
        if defined is None or lemma in defined:
            return lemma

        # we go over the other candidates as a last resort
        for cand in candidates:
            if cand in defined:
                return cand

        # last resort is the porter stem:
        if stem in defined:
            return stem

        # if that doesn't work either, we return None
        return None

    def get_analyzer(self):
        hunmorph_path = self.cfg.get('lemmatizer', 'hunmorph_path')
        ocamorph_fn = os.path.join(hunmorph_path, "ocamorph")
        morphdb_model_fn = os.path.join(hunmorph_path, "morphdb_en.bin")
        hundisambig_fn = os.path.join(hunmorph_path, "hundisambig")
        hunpos_model_fn = os.path.join(hunmorph_path, "en_wsj.model")

        # logging.warning('loading hunmorph...')
        for fn in (ocamorph_fn, morphdb_model_fn, hundisambig_fn,
                   hunpos_model_fn):
            if not os.path.exists(fn):
                raise Exception("can't find hunmorph resource: {0}".format(fn))

        ocamorph = Ocamorph(ocamorph_fn, morphdb_model_fn)
        ocamorph_analyzer = OcamorphAnalyzer(ocamorph)
        hundisambig = Hundisambig(hundisambig_fn, hunpos_model_fn)
        morph_analyzer = MorphAnalyzer(ocamorph, hundisambig)

        return morph_analyzer, ocamorph_analyzer

    def read_cache(self):
        self.clear_cache()
        cache_fn = self.cfg.get('lemmatizer', 'cache_file')
        if not os.path.exists(cache_fn):
            return
        logging.info('reading hunmorph cache...')
        with open(cache_fn) as f_obj:
            for line in f_obj:
                try:
                    fields = line.decode('utf-8').strip().split('\t')
                except (ValueError, UnicodeDecodeError), e:
                    raise Exception('error parsing line in tok2lemma file: \
                        {0}\n{1}'.format(e, line))

                word, stem, lemma = fields[:3]
                candidates = fields[3:]

                self.cache[word] = (stem, lemma, candidates)

        logging.info('done!')

    def write_cache(self):
        cache_fn = self.cfg.get('lemmatizer', 'cache_file')
        logging.info('writing hunmorph cache...')
        with open(cache_fn, 'w') as f_obj:
            for word, (stem, lemma, candidates) in self.cache.iteritems():
                f_obj.write(u"{0}\t{1}\t{2}\t{3}\n".format(
                    word, stem, lemma, "\t".join(candidates)).encode('utf-8'))

        logging.info('done!')

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = get_cfg(cfg_file)
    lemmatizer = Lemmatizer(cfg)
    while True:
        word = raw_input('> ')
        print lemmatizer.lemmatize(word)

if __name__ == "__main__":
    main()
