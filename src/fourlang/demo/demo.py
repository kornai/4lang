import logging
import os
import random
# import sys

from flask import Flask, render_template, request, url_for

from fourlang.corenlp_wrapper import CoreNLPWrapper
from fourlang.utils import draw_dep_graph, draw_text_graph, ensure_dir, get_cfg
from fourlang.dep_to_4lang import DepTo4lang
from fourlang.text_to_4lang import TextTo4lang

from pymachine.utils import MachineTraverser

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

    def get_dep_table(self, sen_deps):
        t = '<table border="1">\n'
        for dep in sen_deps:
            t += "<tr>\n"
            for e in (dep[0], dep[1][0], dep[2][0]):
                t += "<td> {0} </td>".format(e)
            t += "</tr>\n"
        t += '</table>\n'
        return t

    def text_to_4lang(self, text, expand, fn='pic', dep_fn='deps'):
        preproc_sen = TextTo4lang.preprocess_text(text.strip().decode('utf-8'))
        deps, corefs = self.parser_wrapper.parse_text(preproc_sen)
        words2machines = self.dep_to_4lang.get_machines_from_deps_and_corefs(
            deps, corefs)
        # TODO
        orig_machines = set()
        for machine in words2machines.itervalues():
            orig_machines |= set(MachineTraverser.get_nodes(
                machine, names_only=False, keep_upper=True))
        # orig_machines = set([m.printname() for m in words2machines.values()])
        # logging.info(u'orig_machines: {0}'.format(
        #     [m.printname() for m in orig_machines]))
        if expand:
            self.dep_to_4lang.lexicon.expand(words2machines)
        pic_path = draw_text_graph(
            words2machines, self.tmp_dir, fn=fn,
            orig_machines=orig_machines)
        dep_path = draw_dep_graph(deps[0], self.tmp_dir, dep_fn)
        # deps_table = self.get_dep_table(deps[0])
        return os.path.basename(dep_path), os.path.basename(pic_path)

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

app = Flask(__name__, static_folder=demo.tmp_dir)


@app.route('/', methods=['GET'])
def test():
    return render_template('test.html')


@app.route('/dfl', methods=['POST'])
def dfl_demo():
    sen = request.form['text']
    dep_fn, pic_fn = demo.text_to_4lang(sen, True)
    pic_url = url_for(
        'static', filename=pic_fn, nocache=random.randint(0, 9999))
    dep_url = url_for(
        'static', filename=dep_fn, nocache=random.randint(0, 9999))
    return render_template(
        'pic.html', img_url=pic_url, sen=sen, dep_url=dep_url)


@app.route('/tfl', methods=['POST'])
def tfl_demo():
    sen = request.form['text']
    dep_fn, pic_fn = demo.text_to_4lang(sen, True)
    pic_url = url_for(
        'static', filename=pic_fn, nocache=random.randint(0, 9999))
    dep_url = url_for(
        'static', filename=dep_fn, nocache=random.randint(0, 9999))
    return render_template(
        'pic.html', img_url=pic_url, sen=sen, dep_url=dep_url)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
