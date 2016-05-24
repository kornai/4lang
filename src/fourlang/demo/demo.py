import logging
import os
import random
# import sys

from flask import Flask, render_template, request, url_for

from fourlang.corenlp_wrapper import CoreNLPWrapper
from fourlang.utils import draw_dep_graph, draw_text_graph, ensure_dir, get_cfg
from fourlang.dependency_processor import Dependencies
from fourlang.dep_to_4lang import DepTo4lang
from fourlang.dict_to_4lang import DictTo4lang
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
        self.dict_to_4lang = DictTo4lang(self.cfg)
        self.dict_to_4lang.read_dict()

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

    def dict_to_4lang_demo(self, word, fn='pic', dep_fn='deps'):
        if word in self.dep_to_4lang.lexicon.lexicon:
            source = '4lang'
        elif word in self.dep_to_4lang.lexicon.ext_lexicon:
            source = 'ext'
        else:
            # OOV
            return None, None, None, None

        machine = self.dep_to_4lang.lexicon.get_machine(word)
        pic_path = draw_text_graph({word: machine}, self.tmp_dir, fn=fn)

        if source == '4lang':
            return source, None, None, os.path.basename(pic_path)
        else:
            entry = demo.dict_to_4lang.dictionary[word]
            definition = entry['senses'][0]['definition']
            deps = map(Dependencies.parse_dependency, definition['deps'])
            dep_path = draw_dep_graph(deps, self.tmp_dir, dep_fn)
            return source, definition['sen'], os.path.basename(dep_path), os.path.basename(pic_path)  # nopep8

    def text_to_4lang_demo(self, text, expand, fn='pic', dep_fn='deps'):
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

cfg_file = os.path.join(os.environ['FOURLANGPATH'], 'conf/demo.cfg')
cfg = get_cfg(cfg_file)
demo = FourlangDemo(cfg)

app = Flask(__name__, static_folder=demo.tmp_dir)
app.debug = True


@app.route('/', methods=['GET'])
def test():
    return render_template('test.html')


@app.route('/dfl', methods=['POST'])
def dfl_demo():
    word = request.form['word']
    source, sen, dep_fn, pic_fn = demo.dict_to_4lang_demo(word)
    if source is None:
        return 'oov'
        # return render_template('oov.html', word=word)
    pic_url = url_for(
        'static', filename=pic_fn, nocache=random.randint(0, 9999))
    if source == '4lang':
        return render_template('dfl_4lang.html', word=word, img_url=pic_url)
    elif source == 'ext':
        dep_url = url_for(
            'static', filename=dep_fn, nocache=random.randint(0, 9999))
        return render_template(
            'dfl_ext.html', word=word, img_url=pic_url, sen=sen,
            dep_url=dep_url)
    else:
        assert False


@app.route('/tfl', methods=['POST'])
def tfl_demo():
    sen = request.form['text']
    dep_fn, pic_fn = demo.text_to_4lang_demo(sen, True)
    pic_url = url_for(
        'static', filename=pic_fn, nocache=random.randint(0, 9999))
    dep_url = url_for(
        'static', filename=dep_fn, nocache=random.randint(0, 9999))
    return render_template(
        'tfl.html', img_url=pic_url, sen=sen, dep_url=dep_url)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
