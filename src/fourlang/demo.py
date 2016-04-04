import logging
import sys

# from flask import Flask

from corenlp_wrapper import CoreNLPWrapper
from utils import draw_text_graph, ensure_dir, get_cfg
from dep_to_4lang import DepTo4lang
from text_to_4lang import TextTo4lang

__LOGLEVEL__ = 'INFO'


class FourlangDemo():
    def __init__(self, cfg):
        self.cfg = cfg
        tmp_root = cfg.get('demo', 'tmp_root')
        self.tmp_dir = self.get_tmp_dir_name(tmp_root)
        ensure_dir(self.tmp_dir)
        self.parser_wrapper = CoreNLPWrapper(self.cfg)
        self.dep_to_4lang = DepTo4lang(self.cfg)

    def get_tmp_dir_name(self, tmp_root):
        return tmp_root  # TODO

    def text_to_graph(self, text, expand, fn='pic'):
        preproc_sen = TextTo4lang.preprocess_text(text.strip().decode('utf-8'))
        deps, corefs = self.parser_wrapper.parse_text(preproc_sen)
        machines = self.dep_to_4lang.get_machines_from_deps_and_corefs(
            deps, corefs)
        if expand:
            self.dep_to_4lang.lexicon.expand(machines)
        pic_fn = draw_text_graph(machines, self.tmp_dir, fn=fn)
        return pic_fn

    def backend_test(self):
        u_pic_fn = self.text_to_graph(
            'A man stands in the door', False, 'test_unexpanded')
        logging.info('unexpanded pic drawn to {0}'.format(u_pic_fn))
        e_pic_fn = self.text_to_graph(
            'A man stands in the door', True, 'test_expanded')
        logging.info('expanded pic drawn to {0}'.format(e_pic_fn))


def main():
    logging.basicConfig(
        level=__LOGLEVEL__,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None

    cfg = get_cfg(cfg_file)
    demo = FourlangDemo(cfg)
    demo.backend_test()
    # demo.start()

if __name__ == "__main__":
    main()
