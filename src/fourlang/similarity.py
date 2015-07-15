from collections import defaultdict
from ConfigParser import ConfigParser, NoSectionError
import logging
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
from utils import ensure_dir, get_cfg, print_text_graph

class WordSimilarity():
    def __init__(self, cfg):
        try:
            self.batch = cfg.getboolean('similarity_machine', 'batch')
        except NoSectionError:
            self.batch = False

        self.cfg = cfg
        self.lemmatizer = Lemmatizer(cfg)
        self.lexicon_fn = self.cfg.get("machine", "definitions_binary")
        self.lexicon = Lexicon.load_from_binary(self.lexicon_fn)
        self.defined_words = self.lexicon.get_words()
        self.lemma_sim_cache = {}
        self.links_nodes_cache = {}
        self.stopwords = set(nltk_stopwords.words('english'))

    def log(self, string):
        if not self.batch:
            logging.info(string)

    def get_links_nodes(self, machine, use_cache=True):
        if use_cache and machine in self.links_nodes_cache:
            return self.links_nodes_cache[machine]
        self.seen_for_links = set()
        links = set()
        nodes = set()
        for link, node in self._get_links_nodes(machine, depth=0):
            if link is not None:
                links.add(link)
            if node is not None:
                nodes.add(node)
        self.links_nodes_cache[machine] = (links, nodes)
        return links, nodes

    def _get_links_nodes(self, machine, depth):
        if machine in self.seen_for_links or depth > 5:
            return
        self.seen_for_links.add(machine)
        for hypernym in machine.partitions[0]:
            name = hypernym.printname()
            if name == '=AGT' or not name.isupper():
                # if depth == 0 and name not in ("lack", "to"):  # TMP!!!
                yield name, None

            for link, node in self._get_links_nodes(hypernym, depth=depth+1):
                yield link, node

        for link, node in self.get_binary_links_nodes(machine):
            yield link, node

        for node in MachineTraverser.get_nodes(machine):
            yield None, node

    def get_binary_links_nodes(self, machine):
        for parent, partition in machine.parents:
            parent_pn = parent.printname()
            # if not parent_pn.isupper() or partition == 0:
            if partition == 0:
                # haven't seen it yet but possible
                continue
            elif partition == 1:
                links = set([(parent_pn, other.printname())
                            for other in parent.partitions[2]])
                nodes = [m.printname() for m in parent.partitions[2]]
            elif partition == 2:
                links = set([(other.printname(), parent_pn)
                            for other in parent.partitions[1]])
                nodes = [m.printname() for m in parent.partitions[1]]
            else:
                raise Exception(
                    'machine {0} has more than 3 partitions!'.format(machine))

            for link in links:
                yield link, None
            for node in nodes:
                yield None, node

    def link_similarity(self, links1, links2):
        pass

    def contains(self, links, machine):
        pn = machine.printname()
        for link in links:
            if link == pn or (pn in link and isinstance(link, tuple)):
                self.log('link "{0}" is/contains name "{1}"'.format(link, pn))
                return True
        else:
            return False

    def machine_similarity(self, machine1, machine2, sim_type):
        pn1, pn2 = machine1.printname(), machine2.printname()
        self.log(u'machine1: {0}, machine2: {1}'.format(pn1, pn2))
        if sim_type == 'default':
            # sim = harmonic_mean((
            #     self._all_pairs_similarity(machine1, machine2),
            #     self._links_and_nodes_similarity(machine1, machine2)))
            sim = self._links_and_nodes_similarity(machine1, machine2)
            #                                      exclude_nodes=True)  # TMP!!
        elif sim_type == 'all_pairs':
            sim = self._all_pairs_similarity(machine1, machine2)
        elif sim_type == 'links_and_nodes':
            sim = self._links_and_nodes_similarity(machine1, machine2)
        elif sim_type == 'strict_links_and_nodes':
            sim = self._links_and_nodes_similarity(machine1, machine2,
                                                   no_contain_score=True)
        elif sim_type == 'links':
            sim = self._links_and_nodes_similarity(machine1, machine2,
                                                   exclude_nodes=True)
        elif sim_type == 'strict_links':
            sim = self._links_and_nodes_similarity(machine1, machine2,
                                                   exclude_nodes=True,
                                                   no_contain_score=True)
        else:
            raise Exception("unknown similarity type: {0}".format(sim_type))
        return sim

    def _all_pairs_similarity(self, machine1, machine2):
        words1 = set(MachineTraverser.get_nodes(machine1,
                                                exclude_words=self.stopwords))
        words2 = set(MachineTraverser.get_nodes(machine2,
                                                exclude_words=self.stopwords))
        pair_sims_by_word = defaultdict(dict)
        for word1 in words1:
            for word2 in words2:
                sim = self.word_similarity(word1, word2, -1, -1,
                                           sim_type="strict_links_and_nodes")
                pair_sims_by_word[word1][word2] = sim if sim else 0.0
                pair_sims_by_word[word2][word1] = sim if sim else 0.0

        max_sims_by_word = dict((
            (word, my_max(pair_sims_by_word[word].itervalues()))
            for word in words1 | words2))

        sim = average((average((max_sims_by_word[w] for w in words1)),
                       average((max_sims_by_word[w] for w in words2))))
        # sim = max((my_max((max_sims_by_word[w] for w in words1)),
        #            my_max((max_sims_by_word[w] for w in words2))))
        if sim:
            self.log(
                "{0} - {1} all_pairs similarity: {2} based on: {3}".format(
                    machine1.printname(), machine2.printname(), sim,
                    pair_sims_by_word))
        return sim

    def _links_and_nodes_similarity(self, machine1, machine2,
                                    exclude_nodes=False,
                                    no_contain_score=False):
        sim = 0
        links1, nodes1 = self.get_links_nodes(machine1)
        links2, nodes2 = self.get_links_nodes(machine2)
        if not no_contain_score:
            if (self.contains(links1, machine2) or
                    self.contains(links2, machine1)):
                sim = max(sim, 0.35)
            elif (not exclude_nodes) and (self.contains(nodes1, machine2) or
                                          self.contains(nodes2, machine1)):
                sim = max(sim, 0.25)
        # self.log('links1: {0}, links2: {1}'.format(links1, links2))
        # self.log('nodes1: {0}, nodes2: {1}'.format(nodes1, nodes2))
        if True:
            pn1, pn2 = machine1.printname(), machine2.printname()
            if pn1 in links2 or pn2 in links1:
                self.log(
                    "{0} and {1} connected by 0-path, returning 1".format(
                        pn1, pn2))
                return 1
        entities1 = filter(lambda l: "@" in l, links1)
        entities2 = filter(lambda l: "@" in l, links2)
        if entities1 or entities2:
            sim = max(sim, jaccard(entities1, entities2))
        else:
            sim = max(sim, jaccard(links1, links2))
            if not exclude_nodes:
                node_sim = jaccard(nodes1, nodes2)
                if node_sim > sim:
                    self.log(
                        'picking node sim ({0}) over link sim ({1})'.format(
                            node_sim, sim))
                    sim = node_sim

        return sim

    def word_similarity(self, word1, word2, pos1, pos2, sim_type='default',
                        fallback=lambda a, b, c, d: None):
        # self.log(u'words: {0}, {1}'.format(word1, word2))
        lemma1, lemma2 = [self.lemmatizer.lemmatize(
            word, defined=self.defined_words, stem_first=True)
            for word in (word1, word2)]
        # self.log(u'lemmas: {0}, {1}'.format(lemma1, lemma2))
        if lemma1 is None or lemma2 is None:
            return fallback(word1, word2, pos1, pos2)
        sim = self.lemma_similarity(lemma1, lemma2, sim_type)
        return sim

    def lemma_similarity(self, lemma1, lemma2, sim_type):
        if (lemma1, lemma2) in self.lemma_sim_cache:
            return self.lemma_sim_cache[(lemma1, lemma2)]
        elif lemma1 == lemma2:
            return 1
        # self.log(u'lemma1: {0}, lemma2: {1}'.format(lemma1, lemma2))

        machine1, machine2 = map(self.lexicon.get_machine, (lemma1, lemma2))

        sim = self.machine_similarity(machine1, machine2, sim_type)

        self.log(u"S({0}, {1}) = {2}".format(lemma1, lemma2, sim))

        sim = sim if sim >= 0 else 0
        self.lemma_sim_cache[(lemma1, lemma2)] = sim
        self.lemma_sim_cache[(lemma2, lemma1)] = sim
        return sim

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

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")

    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = get_cfg(cfg_file)
    main_sen_sim(cfg)

if __name__ == '__main__':
    # import cProfile
    # cProfile.run('main()')
    main()
