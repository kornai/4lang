from ConfigParser import ConfigParser
import logging
import os

import graphviz
from hunmisc.corpustools.tsv_tools import get_dependencies, sentence_iterator

from pymachine.machine import Machine
from pymachine.utils import MachineGraph


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def batches(l, n):
    """ Yield successive n-sized chunks from l.
    (source: http://stackoverflow.com/questions/312443/
    how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def draw_text_graph(
        words_to_machines, out_dir, fn='text', orig_machines=[]):
    graph = MachineGraph.create_from_machines(
        words_to_machines.values(), orig_machines=orig_machines)
    src_str = graph.to_dot().encode('utf-8')
    src = graphviz.Source(src_str, format='png')
    pic_path = src.render(filename=fn, directory=out_dir)
    return pic_path


def print_text_graph(words_to_machines, graph_dir, fn='text'):
    graph = MachineGraph.create_from_machines(
        words_to_machines.values())
    fn = os.path.join(graph_dir, '{0}.dot'.format(fn))
    with open(fn, 'w') as f:
        f.write(graph.to_dot().encode('utf-8'))
    return fn


def print_4lang_graphs(lexicon, graph_dir):
    logging.info('printing graphs to {0}'.format(graph_dir))
    for word, machine_set in lexicon.iteritems():
        print_4lang_graph(word, next(iter(machine_set)), graph_dir)


def print_4lang_graph(word, machine, graph_dir, max_depth=None):
    graph = MachineGraph.create_from_machines([machine], max_depth=max_depth)
    fn = os.path.join(graph_dir, u"{0}.dot".format(word)).encode('utf-8')
    with open(fn, 'w') as dot_obj:
        dot_obj.write(graph.to_dot().encode('utf-8'))


HEADER = u"digraph finite_state_machine {\n\tdpi=100;\n\trankdir=LR;\n"
EXCLUDE = ("punct")


def dep_to_dot(deps):
    if isinstance(deps[0], dict):
        # new dep structure
        edges = [
            (d['dep']['lemma'], d['type'], d['gov']['lemma']) for d in deps
            if d['type'] not in EXCLUDE]
    else:
        # old dep structure
        edges = [(d[1][0], d[0], d[2][0]) for d in deps if d[0] not in EXCLUDE]

    words = set([e[0] for e in edges] + [e[2] for e in edges])
    lines = []
    for word in words:
        lines.append(u'\t{0} [shape=rectangle, label="{0}"];'.format(
            Machine.d_clean(word)))
    for edge in edges:
        dep, dtype, gov = map(Machine.d_clean, edge)
        lines.append(u'\t{0} -> {1} [label="{2}"];'.format(dep, gov, dtype))

    dot_str = HEADER.encode("utf-8")
    dot_str += u"\n".join(lines).encode("utf-8")
    dot_str += "}\n"
    return dot_str


def draw_dep_graph(deps, out_dir, fn):
    dot_str = dep_to_dot(deps)
    src = graphviz.Source(dot_str, format='png')
    pic_path = src.render(filename=fn, directory=out_dir)
    return pic_path


def get_raw_deps(fn):
    curr_deps = []
    with open(fn) as f:
        for line in f:
            l = line.strip()
            if not l:
                if curr_deps:
                    yield curr_deps
                    curr_deps = []
                continue
            elif l[0] == '(':
                continue
            else:
                curr_deps.append(l)

def conll_to_deps(stream):
    for sen in sentence_iterator(stream):
        yield get_dependencies(sen)


def get_cfg(cfg_file=None):
    cfg_files = [os.path.join(os.environ['FOURLANGPATH'], 'conf/default.cfg')]
    not_found = [fn for fn in cfg_files if not os.path.exists(fn)]
    if cfg_file is not None:
        cfg_files.append(cfg_file)
    if not_found:
        raise Exception("cfg file(s) not found: {0}".format(not_found))
    cfg = ConfigParser(os.environ)
    cfg.read(cfg_files)
    return cfg
