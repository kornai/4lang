from ConfigParser import ConfigParser
import logging
import os

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

def get_cfg(cfg_file=None):
    cfg_files = ['conf/default.cfg']
    not_found = [fn for fn in cfg_files if not os.path.exists(fn)]
    if cfg_file is not None:
        cfg_files.append(cfg_file)
    if not_found:
        raise Exception("cfg file(s) not found: {0}".format(not_found))
    cfg = ConfigParser()
    cfg.read(cfg_files)
    return cfg
