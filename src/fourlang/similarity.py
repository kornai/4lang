from collections import defaultdict
from ConfigParser import ConfigParser, NoSectionError
import logging
import math
import sys

from gensim.models import Word2Vec
from nltk.corpus import stopwords as nltk_stopwords
from scipy.stats.stats import pearsonr

from pymachine.utils import average, harmonic_mean, jaccard, min_jaccard, MachineGraph, MachineTraverser, my_max  # nopep8
from pymachine.wrapper import Wrapper as MachineWrapper
assert jaccard, min_jaccard  # silence pyflakes

from lemmatizer import Lemmatizer
from lexicon import Lexicon
from text_to_4lang import TextTo4lang
from utils import ensure_dir, get_cfg, print_text_graph, print_4lang_graph

class WordSimilarity():
    sim_types = set([
        'links_jaccard', 'nodes_jaccard', 'links_contain', 'nodes_contain',
        '0-connected', 'entities_jaccard'
    ])

    def __init__(self, cfg, cfg_section='word_sim'):
        try:
            self.batch = cfg.getboolean(cfg_section, 'batch')
        except NoSectionError:
            self.batch = False

        self.cfg = cfg
        self.graph_dir = cfg.get(cfg_section, "graph_dir")
        ensure_dir(self.graph_dir)
        self.lemmatizer = Lemmatizer(cfg)
        self.lexicon_fn = self.cfg.get(cfg_section, "definitions_binary")
        self.lexicon = Lexicon.load_from_binary(self.lexicon_fn)
        self.defined_words = self.lexicon.get_words()
        self.word_sim_cache = {}
        self.lemma_sim_cache = {}
        self.links_nodes_cache = {}
        self.stopwords = set(nltk_stopwords.words('english'))
        self.expand = cfg.getboolean(cfg_section, "expand")
        logging.info("expand is {0}".format(self.expand))

    def log(self, string):
        if not self.batch:
            logging.info(string)

    def uniform_similarities(self, s):
        return dict(((sim_type, s) for sim_type in WordSimilarity.sim_types))
        # TODO return {sim_type: s for sim_type in WordSimilarity.sim_types}

    def zero_similarities(self):
        return self.uniform_similarities(0.0)

    def one_similarities(self):
        return self.uniform_similarities(1.0)

    def sim_type_to_function(self, sim_type):
        return lambda w1, w2: self.word_similarities(w1, w2)[sim_type]

    def machine_similarities(self, machine1, machine2):
        pn1, pn2 = machine1.printname(), machine2.printname()
        self.log(u'machine1: {0}, machine2: {1}'.format(pn1, pn2))

        sims = self.zero_similarities()
        links1, nodes1 = self.get_links_nodes(machine1)
        links2, nodes2 = self.get_links_nodes(machine2)
        self.log('links1: {0}, links2: {1}'.format(links1, links2))
        self.log('nodes1: {0}, nodes2: {1}'.format(nodes1, nodes2))
        if (self.contains(links1, machine2) or
                self.contains(links2, machine1)):
            sims['links_contain'] = 1

        if (self.contains(nodes1, machine2) or
                self.contains(nodes2, machine1)):
            sims['nodes_contain'] = 1

        pn1, pn2 = machine1.printname(), machine2.printname()
        # TODO
        if pn1 in links2 or pn2 in links1:
            sims['0-connected'] = 1

        entities1 = filter(lambda l: "@" in l, links1)
        entities2 = filter(lambda l: "@" in l, links2)
        sims['entities_jaccard'] = jaccard(entities1, entities2)

        sims['links_jaccard'] = jaccard(links1, links2)
        sims['nodes_jaccard'] = jaccard(nodes1, nodes2)

        return sims

    def lemma_similarities(self, lemma1, lemma2):
        if (lemma1, lemma2) in self.lemma_sim_cache:
            return self.lemma_sim_cache[(lemma1, lemma2)]

        if lemma1 == lemma2:
            lemma_sims = self.one_similarities()

        if self.expand:
            machine1, machine2 = map(
                self.lexicon.get_expanded_definition, (lemma1, lemma2))
        else:
            machine1, machine2 = map(
                self.lexicon.get_machine, (lemma1, lemma2))

        if not self.batch:
            for w, m in ((lemma1, machine1), (lemma2, machine2)):
                print_4lang_graph(w, m, self.graph_dir)
        lemma_sims = self.machine_similarities(machine1, machine2)
        self.lemma_sim_cache[(lemma1, lemma2)] = lemma_sims
        self.lemma_sim_cache[(lemma2, lemma1)] = lemma_sims
        return lemma_sims

    def word_similarities(self, word1, word2):
        if (word1, word2) in self.word_sim_cache:
            return self.word_sim_cache[(word1, word2)]
        lemma1, lemma2 = [self.lemmatizer.lemmatize(
            word, defined=self.defined_words, stem_first=True)
            for word in (word1, word2)]
        # self.log(u'lemmas: {0}, {1}'.format(lemma1, lemma2))
        if lemma1 is None or lemma2 is None:
            if lemma1 is None:
                logging.debug("OOV: {0}".format(word1))
            if lemma2 is None:
                logging.debug("OOV: {0}".format(word2))
            # TODO
            word_sims = self.zero_similarities()
        else:
            word_sims = self.lemma_similarities(lemma1, lemma2)
        self.word_sim_cache[(word1, word2)] = word_sims
        self.word_sim_cache[(word2, word1)] = word_sims
        return word_sims

    def get_links_nodes(self, machine, use_cache=True):
        if use_cache and machine in self.links_nodes_cache:
            return self.links_nodes_cache[machine]
        self.seen_for_links = set()
        links, nodes = self._get_links_and_nodes(machine, depth=0)
        links, nodes = set(links), set(nodes)
        links.add(machine.printname())
        nodes.add(machine.printname())
        self.links_nodes_cache[machine] = (links, nodes)
        return links, nodes

    def _get_links_and_nodes(self, machine, depth, exclude_links=False):
        name = machine.printname()
        if name.isupper() or name == '=AGT':
            links, nodes = [], []
        elif exclude_links:
            links, nodes = [], [name]
        else:
            links, nodes = [name], [name]

        # logging.info("{0}{1},{2}".format(depth*"    ", links, nodes))
        is_negated = False
        if machine in self.seen_for_links or depth > 5:
            return [], []
        self.seen_for_links.add(machine)
        for i, part in enumerate(machine.partitions):
            for hypernym in part:
                h_name = hypernym.printname()
                # logging.info("{0}h: {1}".format(depth*"    ", h_name))
                if h_name in ("lack", "not"):
                    is_negated = True
                    continue

                c_links, c_nodes = self._get_links_and_nodes(
                    hypernym, depth=depth+1, exclude_links=i != 0)

                if not h_name.isupper():
                    links += c_links
                nodes += c_nodes

        if not exclude_links:
            links += self.get_binary_links(machine)
        if is_negated:
            add_lack = lambda link: "lack_{0}".format(link) if isinstance(link, unicode) else ("lack_{0}".format(link[0]), link[1])  # nopep8
            links = map(add_lack, links)
            nodes = map(add_lack, nodes)

        return links, nodes

    def get_binary_links(self, machine):
        for parent, partition in machine.parents:
            parent_pn = parent.printname()
            # if not parent_pn.isupper() or partition == 0:
            if partition == 0:
                # haven't seen it yet but possible
                continue
            elif partition == 1:
                links = set([(parent_pn, other.printname())
                            for other in parent.partitions[2]])
            elif partition == 2:
                links = set([(other.printname(), parent_pn)
                            for other in parent.partitions[1]])
            else:
                raise Exception(
                    'machine {0} has more than 3 partitions!'.format(machine))
            for link in links:
                yield link

    def contains(self, links, machine):
        pn = machine.printname()
        for link in links:
            if link == pn or (pn in link and isinstance(link, tuple)):
                self.log('link "{0}" is/contains name "{1}"'.format(link, pn))
                return True
        else:
            return False

class GraphSimilarity():
    @staticmethod
    def graph_similarity(graph1, graph2):
        return jaccard(graph1.edges, graph2.edges)

    @staticmethod
    def old_graph_similarity(graph1, graph2):
        sim1, ev1 = GraphSimilarity.supported_score(graph1, graph2)
        sim2, ev2 = GraphSimilarity.supported_score(graph2, graph1)
        if sim1 + sim2 > 0:
            pass
            # logging.info('evidence sets: {0}, {1}'.format(ev2, ev2))
        return harmonic_mean((sim1, sim2))

    @staticmethod
    def supported_score(graph, context_graph):
        edge_count = len(graph.edges)
        supported = graph.edges.intersection(context_graph.edges)
        return len(supported) / float(edge_count), supported

    @staticmethod
    def old_supported_score(graph, context_graph):
        zero_count, zero_supported, bin_count, bin_supported = 0, 0, 0, 0
        evidence = []
        binaries = defaultdict(set)
        # logging.info('context edges: {0}'.format(context_graph.edges))
        for edge in graph.edges:
            # logging.info('testing edge: {0}'.format(edge))
            if edge[2] == 0:
                zero_count += 1
                if edge in context_graph.edges:
                    # logging.info('supported 0-edge: {0}'.format(edge))
                    evidence.append(edge)
                    zero_supported += 1
            else:
                binaries[edge[0]].add(edge)

        for binary, edges in binaries.iteritems():
            bin_count += 1
            if all(edge in context_graph.edges for edge in edges):
                # logging.info('supported binary: {0}'.format(edges))
                evidence.append(edges)
                bin_supported += 1

        if zero_count + bin_count == 0:
            logging.warning("nothing to support: {0}".format(graph))
            return 0.0, []

        return (zero_supported + bin_supported) / float(
            zero_count + bin_count), evidence

class SimComparer():
    def __init__(self, cfg_file, batch=True):
        self.config_file = cfg_file
        self.config = ConfigParser()
        self.config.read(cfg_file)
        self.get_vec_sim()
        self.get_machine_sim(batch)

    def get_vec_sim(self):
        model_fn = self.config.get('vectors', 'model')
        model_type = self.config.get('vectors', 'model_type')
        logging.warning('Loading model: {0}'.format(model_fn))
        if model_type == 'word2vec':
            self.vec_model = Word2Vec.load_word2vec_format(model_fn,
                                                           binary=True)
        elif model_type == 'gensim':
            self.vec_model = Word2Vec.load(model_fn)
        else:
            raise Exception('Unknown LSA model format')
        logging.warning('Model loaded: {0}'.format(model_fn))

    def vec_sim(self, w1, w2):
        if w1 in self.vec_model and w2 in self.vec_model:
            return self.vec_model.similarity(w1, w2)
        return None

    def get_machine_sim(self, batch):
        wrapper = MachineWrapper(
            self.config_file, include_longman=True, batch=batch)
        self.sim_wrapper = WordSimilarity(wrapper)

    def sim(self, w1, w2):
        return self.sim_wrapper.word_similarity(w1, w2, -1, -1)

    def get_words(self):
        self.words = set((
            line.strip().decode("utf-8") for line in open(
                self.config.get('words', 'word_file'))))
        logging.warning('read {0} words'.format(len(self.words)))

    def get_machine_sims(self):
        sim_file = self.config.get('machine', 'sim_file')
        self.machine_sims = {}
        out = open(sim_file, 'w')
        count = 0
        for w1, w2 in self.sorted_word_pairs:
            if count % 100000 == 0:
                logging.warning("{0} pairs done".format(count))
            sim = self.sim(w1, w2)
            if sim is None:
                logging.warning(
                    u"sim is None for non-ooovs: {0} and {1}".format(w1, w2))
                logging.warning("treating as 0 to avoid problems")
                self.machine_sims[(w1, w2)] = 0
            else:
                self.machine_sims[(w1, w2)] = sim
            count += 1
            out.write(
                u"{0}_{1}\t{2}\n".format(w1, w2, sim).encode('utf-8'))
        out.close()

    def get_vec_sims(self):
        sim_file = self.config.get('vectors', 'sim_file')
        out = open(sim_file, 'w')
        self.vec_sims = {}
        for w1, w2 in self.sorted_word_pairs:
            vec_sim = self.vec_sim(w1, w2)
            self.vec_sims[(w1, w2)] = vec_sim
            out.write(
                u"{0}_{1}\t{2}\n".format(w1, w2, vec_sim).encode('utf-8'))
        out.close()

    def get_sims(self):
        self.get_words()
        self.non_oov = set(
            (word for word in self.words if word in self.vec_model))

        logging.warning(
            'kept {0} words after discarding those not in embedding'.format(
                len(self.non_oov)))

        logging.warning('lemmatizing words to determine machine-OOVs...')
        self.non_oov = set(
            (word for word in self.non_oov
                if self.sim_wrapper.lemmatizer.lemmatize(
                    word, defined=self.sim_wrapper.machine_wrapper.definitions,
                    stem_first=True) is not None))

        logging.warning(
            'kept {0} words after discarding those not in machine sim'.format(
                len(self.non_oov)))

        self.sorted_word_pairs = set()
        for w1 in self.non_oov:
            for w2 in self.non_oov:
                if w1 != w2 and w1 == sorted([w1, w2])[0]:
                    self.sorted_word_pairs.add((w1, w2))

        self.get_machine_sims()
        self.get_vec_sims()

    def compare(self):
        sims = [self.machine_sims[pair] for pair in self.sorted_word_pairs]
        vec_sims = [self.vec_sims[pair] for pair in self.sorted_word_pairs]

        pearson = pearsonr(sims, vec_sims)
        print "compared {0} distance pairs.".format(len(sims))
        print "Pearson-correlation: {0}".format(pearson)

def main_compare(cfg):
    comparer = SimComparer(cfg)
    comparer.get_sims()
    comparer.compare()

def main_sen_sim(cfg):
    graph_dir = cfg.get("sim", "graph_dir")
    dep_dir = cfg.get("sim", "deps_dir")
    ensure_dir(graph_dir)
    ensure_dir(dep_dir)

    text_to_4lang = TextTo4lang(cfg)
    for i, line in enumerate(sys.stdin):
        preprocessed_line = line.decode('utf-8').strip().lower()
        sen1, sen2 = preprocessed_line.split('\t')
        machines1 = text_to_4lang.process(
            sen1, dep_dir=dep_dir, fn="{0}a".format(i))
        machines2 = text_to_4lang.process(
            sen2, dep_dir=dep_dir, fn="{0}b".format(i))

        print_text_graph(machines1, graph_dir, fn="{0}a".format(i))
        print_text_graph(machines2, graph_dir, fn="{0}b".format(i))

        graph1, graph2 = map(
            MachineGraph.create_from_machines,
            (machines1.values(), machines2.values()))
        print GraphSimilarity.graph_similarity(graph1, graph2)

    # text_to_4lang.dep_to_4lang.lemmatizer.write_cache()


def get_test_pairs(fn):
    pairs = {}
    for line in open(fn):
        w1, w2, sim_str = line.decode('utf-8').strip().split('\t')
        pairs[(w1, w2)] = float(sim_str) / 10
    return pairs

def main_word_test(cfg):
    from scipy.stats.stats import pearsonr
    word_sim = WordSimilarity(cfg)
    test_pairs = get_test_pairs(cfg.get('sim', 'word_test_data'))
    sims, gold_sims = [], []
    for (w1, w2), gold_sim in test_pairs.iteritems():
        sim = word_sim.word_similarity(w1, w2, 'foo', 'foo')  # dummy POS-tags
        if sim is None:
            continue
        gold_sims.append(gold_sim)
        sims.append(sim)
        print "{0}\t{1}\t{2}\t{3}\t{4}".format(
            w1, w2, gold_sim, sim, math.fabs(sim-gold_sim))

    print "Pearson: {0}".format(pearsonr(gold_sims, sims))

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")

    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = get_cfg(cfg_file)
    sim_type = cfg.get('sim', 'similarity_type')
    if sim_type == 'sentence':
        main_sen_sim(cfg)
    elif sim_type == 'word':
        raise Exception("main function for word sim not implemented yet")
    elif sim_type == 'word_test':
        main_word_test(cfg)
    else:
        raise Exception('unknown similarity type: {0}'.format(sim_type))

if __name__ == '__main__':
    # import cProfile
    # cProfile.run('main()')
    main()
