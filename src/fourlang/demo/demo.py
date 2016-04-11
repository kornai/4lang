import logging
import os
# import sys

from flask import Flask, render_template, request  # , url_for

from fourlang.corenlp_wrapper import CoreNLPWrapper
from fourlang.utils import draw_text_graph, ensure_dir, get_cfg
from fourlang.dep_to_4lang import DepTo4lang
from fourlang.text_to_4lang import TextTo4lang

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
        pic_fn = draw_text_graph(machines, 'static', fn=fn)  # TODO
        return os.path.basename(pic_fn)

    def backend_test(self):
        u_pic_fn = self.text_to_graph(
            'A man stands in the door', False, 'test_unexpanded')
        logging.info('unexpanded pic drawn to {0}'.format(u_pic_fn))
        e_pic_fn = self.text_to_graph(
            'A man stands in the door', True, 'test_expanded')
        logging.info('expanded pic drawn to {0}'.format(e_pic_fn))


logging.basicConfig(
    level=__LOGLEVEL__,
    format="%(asctime)s : " +
    "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")

cfg = get_cfg(None)
demo = FourlangDemo(cfg)

app = Flask(__name__)
# app = Flask(__name__, static_path=demo.tmp_dir)


@app.route('/', methods=['GET'])
def test():
    return render_template('test.html')


@app.route('/process', methods=['POST'])
def process():
    pic_fn = demo.text_to_graph(request.form['text'], True)
    # pic_url = url_for('static', filename=pic_fn)
    pic_url = 'static/{0}'.format(pic_fn)
    # return render_template('pic.html', img_url=pic_fn)
    return render_template('pic.html', img_url=pic_url)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
