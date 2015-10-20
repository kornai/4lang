import logging
import os
import re
import sys
import pdb

from corenlp_wrapper import CoreNLPWrapper
from dep_to_4lang import DepTo4lang, Dependency
from lexicon import Lexicon
from utils import ensure_dir, get_cfg, print_text_graph

assert Lexicon  # silence pyflakes (Lexicon must be imported for cPickle)

__LOGLEVEL__ = 'DEBUG'
__MACHINE_LOGLEVEL__ = 'INFO'

class TextTo4lang():
    square_regex = re.compile("\[.*?\]")

    def __init__(self, cfg):
        self.cfg = cfg
        self.lang = self.cfg.get("deps", "lang")
        self.deps_dir = self.cfg.get('data', 'deps_dir')
        ensure_dir(self.deps_dir)
        self.corenlp_wrapper = CoreNLPWrapper(self.cfg)
        self.dep_to_4lang = DepTo4lang(self.cfg)

    @staticmethod
    def preprocess_text(text):
        t = text.strip()
        t = TextTo4lang.square_regex.sub('', t)
        t = t.replace(u"=", u"_eq_")
        t = t.replace(u"\xc2\xa0", u" ")
        t = t.replace(u"\xa0", u" ")
        t = t.strip()
        if t != text:
            logging.debug(u"{0} -> {1}".format(text, t))
        return t

    def print_deps(self, parsed_sens, dep_dir=None, fn=None):
        for i, deps in enumerate(parsed_sens):
            if fn is None:
                out_fn = os.path.join(dep_dir, "{0}.dep".format(i))
            else:
                out_fn = os.path.join(dep_dir, "{0}_{1}.dep".format(fn, i))
            with open(out_fn, 'w') as f:
                f.write(
                    "\n".join(["{0}({1}, {2})".format(*dep) for dep in deps]))

    def process(self, text, dep_dir=None, fn=None):
        # logging.info("running parser...")
        preproc_text = TextTo4lang.preprocess_text(text)
        # logging.info('preproc text: {0}'.format(repr(preproc_text)))
        parsed_sens, corefs = self.corenlp_wrapper.parse_text(preproc_text) 
        
        # logging.info("parsed {0} sentences".format(len(parsed_sens)))
        if dep_dir is not None:
            self.print_deps(parsed_sens, dep_dir, fn)

        # logging.info("loading dep_to_4lang...")
        logging.getLogger().setLevel(__MACHINE_LOGLEVEL__)

        # logging.info("processing sentences...")
        if self.lang == 'en':
            parsed_sens = map(
                self.dep_to_4lang.convert_old_deps, parsed_sens)
        words_to_machines = self.dep_to_4lang.get_machines_from_deps_and_corefs(  # nopep8
            parsed_sens, corefs)

        # logging.info(
        #      "done, processed {0} sentences".format(len(parsed_sens)))

        return words_to_machines
    @staticmethod
    def delete_connection(m1,m2):
        for part in range(len(m1.partitions)):
            if len(m1.partitions[part])>0 and m1.partitions[part][0]==m2:
                m1.remove(m2,part)
    
    def expand(self, words_to_machines, stopwords = []):
        if len(stopwords) == 0:
            stopwords = set(self.dep_to_4lang.lexicon.lexicon.keys())
        known_words=self.dep_to_4lang.lexicon.get_words()
        for lemma, machine in words_to_machines.iteritems():
            if lemma in known_words and lemma not in stopwords:
                # sys.stderr.write(lemma + "\t")
                definition=self.dep_to_4lang.lexicon.get_machine(lemma)
                if len(definition.children())==1 and len(definition.parents) ==0:
                    def_head = next(iter(definition.children()))
                    parents = machine.parents
                    children = machine.children()
                    for p in list(parents):
                        TextTo4lang.delete_connection(p[0], machine)
                        p[0].append(def_head, 1)
                    for ch in children:
                        def_head.append(ch[0], 1)
                    TextTo4lang.delete_connection(definition, def_head)
        return

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
    sens = [line.decode('utf-8').strip() for line in open(input_fn)]
    if max_sens is not None:
        sens = sens[:max_sens]

    words_to_machines = text_to_4lang.process(
        "\n".join(sens), dep_dir=text_to_4lang.deps_dir)
    text_to_4lang.expand(words_to_machines, set(text_to_4lang.dep_to_4lang.lexicon.lexicon.keys()) | set(["the"]))
    
    graph_dir = cfg.get('machine', 'graph_dir')
    ensure_dir(graph_dir)
    fn = print_text_graph(words_to_machines, graph_dir)
    logging.info('wrote graph to {0}'.format(fn))
    
if __name__ == "__main__":
    main()
