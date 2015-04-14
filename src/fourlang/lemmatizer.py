import logging
import os

from hunmisc.utils.huntool_wrapper import Hundisambig, Ocamorph, OcamorphAnalyzer, MorphAnalyzer  # nopep8
from stemming.porter2 import stem

class Lemmatizer():

    def __init__(self, cfg):
        self.cfg = cfg
        self.analyzer, self.morph_analyzer = self.get_analyzer()
        self.tok2lemma = {}
        # self.tok2lemma = Wrapper.get_tok2lemma(self.tok2lemma_fn)
        self.oov = set()

    def empty_cache(self):
        self.tok2lemma = {}
        self.oov = set()

    def lemmatize(self, word, defined=None, stem_first=False,
                  debug=False):
        # if 'defined' is provided, will refuse to return lemmas not in it

        # we check if the word is in either of our caches
        if word in self.tok2lemma:
            return self.tok2lemma[word]
        elif word in self.oov:
            if defined is not None:
                return None
            return word

        if debug:
            tried = []
        if stem_first:
            stemmed_word = stem(word)
            if debug:
                tried.append(stemmed_word)
            stemmed_lemma = self.get_lemma(
                stemmed_word, defined=defined, stem_first=False)
            if stemmed_lemma is not None:
                self.tok2lemma[word] = stemmed_lemma
                return stemmed_lemma

        if defined is not None and word in defined:
            self.tok2lemma[word] = word
            return word

        disamb_lemma = list(self.analyzer.analyze(
            [[word]]))[0][0][1].split('||')[0].split('<')[0]

        if defined is None or disamb_lemma in defined:
            self.tok2lemma[word] = disamb_lemma
        else:
            if debug:
                tried.append(disamb_lemma)
            candidates = self.morph_analyzer.analyze([[word]]).next().next()
            for cand in candidates:
                lemma = cand.split('||')[0].split('<')[0]
                if debug:
                    tried.append(lemma)
                if lemma in defined:
                    self.tok2lemma[word] = lemma
                    break
            else:
                if debug:
                    logging.info('new OOV: {0} (tried these: {1})'.format(
                        word, tried))
                self.oov.add(word)
                return None

        return self.tok2lemma[word]

    def get_analyzer(self):
        hunmorph_path = self.cfg.get('lemmatizer', 'hunmorph_path')
        ocamorph = Ocamorph(
            os.path.join(hunmorph_path, "ocamorph"),
            os.path.join(hunmorph_path, "morphdb_en.bin"))
        ocamorph_analyzer = OcamorphAnalyzer(ocamorph)
        morph_analyzer = MorphAnalyzer(
            ocamorph,
            Hundisambig(
                os.path.join(hunmorph_path, "hundisambig"),
                os.path.join(hunmorph_path, "en_wsj.model")))

        return morph_analyzer, ocamorph_analyzer

    @staticmethod
    def get_tok2lemma(tok2lemma_fn):
        tok2lemma = {}
        if tok2lemma_fn is None:
            return tok2lemma
        for line in file(tok2lemma_fn):
            try:
                tok, lemma = line.decode('utf-8').strip().split('\t')
            except (ValueError, UnicodeDecodeError), e:
                raise Exception(
                    'error parsing line in tok2lemma file: {0}\n{1}'.format(
                        e, line))
            tok2lemma[tok] = lemma

        return tok2lemma

def main():
    pass

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    main()
