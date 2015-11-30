import json
import logging
import os
import re
import sys

from corenlp_wrapper import CoreNLPWrapper
from dep_to_4lang import DepTo4lang
from lexicon import Lexicon
from magyarlanc_wrapper import Magyarlanc
from utils import ensure_dir, get_cfg, print_text_graph

assert Lexicon  # silence pyflakes (Lexicon must be imported for cPickle)

__LOGLEVEL__ = 'INFO'
__MACHINE_LOGLEVEL__ = 'INFO'

class TextTo4lang():
    square_regex = re.compile("\[.*?\]")

    def __init__(self, cfg):
        self.cfg = cfg
        self.lang = self.cfg.get("deps", "lang")
        self.deps_dir = self.cfg.get('text', 'deps_dir')
        # self.machines_dir = self.cfg.get('text', 'machines_dir')
        self.graphs_dir = cfg.get('text', 'graph_dir')
        map(ensure_dir, (self.deps_dir, self.graphs_dir))  # self.machines_dir
        if self.lang == 'en':
            self.parser_wrapper = CoreNLPWrapper(self.cfg)
        elif self.lang == 'hu':
            self.parser_wrapper = Magyarlanc(self.cfg)
        self.dep_to_4lang = DepTo4lang(self.cfg)

    @staticmethod
    def preprocess_text(text):
        t = text.strip()
        t = TextTo4lang.square_regex.sub('', t)
        t = t.replace(u"=", u"_eq_")
        t = t.replace(u"\xc2\xa0", u" ")
        t = t.replace(u"\xa0", u" ")
        t = t.strip()
        # if t != text:
        #   logging.debug(u"{0} -> {1}".format(text, t))
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

    def process(self):
        input_path = self.cfg.get('text', 'input_sens')
        if os.path.isdir(input_path):
            file_names = [
                os.path.join(input_path, fn) for fn in os.listdir(input_path)]
        else:
            file_names = [input_path]
        logging.info('will process {0} file(s)'.format(len(file_names)))
        map(self.process_file, file_names)

    def process_file(self, fn):
        base_fn = os.path.basename(fn)
        deps_fn = os.path.join(self.deps_dir, "{0}.deps".format(base_fn))
        # machines_fn = os.path.join(
        #     self.machines_dir, "{0}.machines".format(base_fn))
        if not os.path.exists(deps_fn):
            self.parse_file(fn, deps_fn)
        else:
            logging.info('file exists: {0}, not parsing'.format(deps_fn))

        # TODO also support dumping machines to file
        # logging.getLogger().setLevel(__MACHINE_LOGLEVEL__)

        if not self.cfg.getboolean('text', 'parse_only'):
            self.process_deps(deps_fn)

    def parse_file(self, fn, out_fn):
        logging.info("parsing file: {0}".format(fn))
        preproc_sens = []
        for line in open(fn):
            if not line:
                continue
            preproc_sens.append(TextTo4lang.preprocess_text(
                line.strip().decode('utf-8')))
        deps, corefs = self.parser_wrapper.parse_text("\n".join(preproc_sens))
        with open(out_fn, 'w') as out_f:
            out_f.write("{0}\n".format(json.dumps({
                "deps": deps,
                "corefs": corefs})))
        logging.info("parsed {0} sentences".format(len(deps)))

    def process_deps(self, fn):
        sen_machines = []
        c = 0
        for line in open(fn):
            data = json.loads(line)
            deps, corefs = data['deps'], data['corefs']
            for sen_deps in deps:
                # logging.info("processing sentences...")
                machines = self.dep_to_4lang.get_machines_from_deps_and_corefs(
                    [sen_deps], corefs)
                if self.cfg.getboolean('text', 'expand'):
                    self.expand(
                        machines,
                        set(self.dep_to_4lang.lexicon.lexicon.keys()) | set(["the"]))  # nopep8

                if self.cfg.getboolean('text', 'print_graphs'):
                    fn = print_text_graph(machines, self.graphs_dir, fn=c)

                sen_machines.append(machines)
                c += 1

        return sen_machines

    @staticmethod
    def delete_connection(m1, m2):
        for part in range(len(m1.partitions)):
            if m2 in m1.partitions[part]:
                m1.remove(m2, part)
                return part
        # ipdb.set_trace()
        return None

    def expand(self, words_to_machines, stopwords=[]):
        if len(stopwords) == 0:
            stopwords = set(self.dep_to_4lang.lexicon.lexicon.keys())
        known_words = self.dep_to_4lang.lexicon.get_words()
        for lemma, machine in words_to_machines.iteritems():
            if lemma in known_words and lemma not in stopwords:
                definition = self.dep_to_4lang.lexicon.get_machine(lemma)
                machine.unify(definition)
                """
                if (len(definition.children()) == 1 and
                        len(definition.parents) == 0):
                    def_head = next(iter(definition.children()))
                    parents = machine.parents
                    for p in list(parents):
                        part = TextTo4lang.delete_connection(p[0], machine)
                        p[0].append(def_head, part)

                    for part in range(len(machine.partitions)):
                        for ch in machine.partitions[part]:
                            def_head.append(ch, part)
                    TextTo4lang.delete_connection(definition, def_head)
                """
        return

def main():
    logging.basicConfig(
        level=__LOGLEVEL__,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None

    cfg = get_cfg(cfg_file)
    text_to_4lang = TextTo4lang(cfg)
    text_to_4lang.process()

if __name__ == "__main__":
    main()
