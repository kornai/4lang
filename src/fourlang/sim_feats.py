import logging
from pymachine.utils import MachineGraph, jaccard

import networkx as nx
import networkx.algorithms.isomorphism as iso
import itertools
import os.path

class SimFeatures:
    def __init__(self, cfg, section, lexicon):
        self.lexicon = lexicon
        self.batch = cfg.getboolean(section, 'batch')
        self.feats_to_get = cfg.get(section, 'sim_types').split('|')
        self.feats_dict = {
            'links_jaccard' : ['links_jaccard'],
            'entities_jaccard' : ['entities_jaccard'],
            'nodes_jaccard' : ['nodes_jaccard'],
            'links_contain' : ['links_contain'],
            'nodes_contain' : ['nodes_contain'],
            '0-connected' : ['0-connected'],
            'is_antonym' : ['is_antonym'],
            'subgraphs' : ['subgraph_3N'],
            'fullgraph' : ['shortest_path']
        }

        self.shortest_path_file_name = cfg.get(section, 'shortest_path_res')
        if not os.path.isfile(self.shortest_path_file_name) or cfg.getboolean(section, 'calc_shortest_path'):
            self.calc_path = True
            shortest_path_dir = os.path.dirname(self.shortest_path_file_name)
            if not os.path.exists(shortest_path_dir):
                os.makedirs(shortest_path_dir)
            self.shortest_path_res = open(self.shortest_path_file_name, 'w')
        else:
            self.calc_path = False


        if 'fullgraph' in self.feats_to_get:
            self.full_graph = self.lexicon.get_full_graph()
            print "NODES count: {0}".format(len(self.full_graph.nodes()))
            print "EDGES count: {0}".format(len(self.full_graph.edges()))
            self.UG = self.full_graph.to_undirected()

    def get_all_features(self, graph1, graph2):
        all_feats = dict()
        for f in self.feats_to_get:
            all_feats.update(self.get_feature_class(f, graph1, graph2))
        return all_feats

    def get_feature_class(self, feature_name, graph1, graph2):
        if feature_name == 'links_jaccard':
            return self.links_jaccard(graph1.links_expand, graph2.links_expand)
        elif feature_name == 'entities_jaccard':
            return self.entitiess_jaccard(graph1.links_expand, graph2.links_expand)
        elif feature_name == 'nodes_jaccard':
            return self.nodes_jaccard(graph1.nodes_expand, graph2.nodes_expand)
        elif feature_name == 'links_contain':
            return self.links_contain(graph1.name, graph1.links_expand, graph2.name, graph2.links_expand)
        elif feature_name == 'nodes_contain':
            return self.nodes_contain(graph1.name, graph1.nodes_expand, graph2.name, graph2.nodes_expand)
        elif feature_name == '0-connected':
            return self.zero_connected(graph1.name, graph1.links, graph1.links_expand,
                                       graph2.name, graph2.links, graph2.links_expand)
        elif feature_name == 'is_antonym':
            return self.is_antonym(graph1.name, graph1.nodes_expand, graph2.name, graph2.nodes_expand)
        elif feature_name == 'subgraphs':
            return self.subgraphs(graph1.machine, graph2.machine)
        elif feature_name == 'fullgraph':
            return self.fullgraph(graph1.name, graph2.name)
        else:
            return { feature_name : 0 }

    def links_jaccard(self, links1, links2):
        return { "links_jaccard" : jaccard(links1, links2)}

    def entitiess_jaccard(self, links1, links2):
        entities1 = filter(lambda l: "@" in l, links1)
        entities2 = filter(lambda l: "@" in l, links2)
        return {'entities_jaccard' : jaccard(entities1, entities2)}

    def nodes_jaccard(self, nodes1, nodes2):
        return { "nodes_jaccard" : jaccard(nodes1, nodes2)}

    def links_contain(self, name1, links1, name2, links2):
        val = -1
        if (self.contains(links1, name2) or
                self.contains(links2, name1)):
            val = 1
        return { "links_contain" : val}

    def nodes_contain(self, name1, nodes1, name2, nodes2):
        val = -1
        if (self.contains(nodes1, name2) or
                self.contains(nodes2, name1)):
            val = 1
        return { "nodes_contain" : val}

    def zero_connected(self, name1, links1, links1_expand, name2, links2, links2_expand):
        val = -1
        if name1 in links2 or name2 in links1:
            val = 1
        ret = { "0-connected" : val }
        val2 = -1
        if val == -1:
            if name1 in links2_expand or name2 in links1_expand:
                val2 = 1
        return ret

    def is_antonym(self, name1, nodes1, name2, nodes2):
        is_antonym = -1
        if ("lack_" + name1 in nodes2 and name1 not in nodes2):
            is_antonym = 1
        elif("lack_" + name2 in nodes1 and name2 not in nodes1):
            is_antonym = 1
        return {"is_antonym" : is_antonym }

    def subgraphs(self, machine1, machine2):
        temp = SubGraphFeatures(machine1, machine2, 5)
        return temp.subgraph_dict

    def fullgraph(self, name1, name2):
        ####################
        # Only for calculating shortest path
        ####################
        if self.calc_path:
            length = 0
            if name1 not in self.UG.nodes() or name2 not in self.UG.nodes():
                return {"shortest_path" : length}
            if nx.has_path(self.UG, name1, name2):
                path = nx.shortest_path(self.UG, name1, name2)
                length = len(path)
                print "PATH: " + name1 + " " + name2
                print path
                print length
                self.shortest_path_res.write("\t".join(path))
                self.shortest_path_res.write("\n")
        else:
            length = self.lexicon.get_shortest_path(name1, name2, self.shortest_path_file_name)
        return {"shortest_path" : length}

    def contains(self, links, name):
        for link in links:
            if link == name or (name in link and isinstance(link, tuple)):
                self.log('link "{0}" is/contains name "{1}"'.format(link, name))
                return True
        else:
            return False

    def uniform_similarities(self, s):
        temp_dict = dict()
        for sim_type in self.feats_to_get:
            for feat_type in self.feats_dict[sim_type]:
                temp_dict[feat_type] = s
        return temp_dict

    def zero_similarities(self):
        return self.uniform_similarities(0.0)

    def one_similarities(self):
        return self.uniform_similarities(1.0)

    def log(self, string):
        if not self.batch:
            logging.info(string)

class MachineInfo():
    def __init__(self, machine, nodes, nodes_expand, links, links_expand):
        self.name = machine.printname()
        self.machine = machine
        self.nodes = nodes
        self.links = links
        self.nodes_expand = nodes_expand
        self.links_expand = links_expand

class SubGraphFeatures():
    def __init__(self, machine1, machine2, max_depth):
        G1 = MachineGraph.create_from_machines([machine1], max_depth=max_depth)
        G2 = MachineGraph.create_from_machines([machine2], max_depth=max_depth)
        name1 = machine1.printname()
        name2 = machine2.printname()

        self.subgraph_dict = dict()
        # self.subgraph_dict.update(self._get_subgraph_N(G1.G, G2.G, name1, name2))
        # self.subgraph_dict.update(self._get_subgraph_N_X_N(G1.G, G2.G, name1, name2))
        self.subgraph_dict.update(self._get_subgraph_3_nodes(G1.G, G2.G, name1, name2))

    # TODO: not useful
    def _get_subgraph_N(self, graph1, graph2, name1, name2):
        ret = 0
        subgraphs1 = self._get_subgraphs(graph1, name1, 1)
        subgraphs2 = self._get_subgraphs(graph2, name2, 1)

        for r in itertools.product(subgraphs1, subgraphs2):
            GM =  nx.algorithms.isomorphism.GraphMatcher(r[0], r[1],
                                                         node_match=iso.categorical_node_match(['str_name'], ['name']),
                                                         edge_match=iso.numerical_edge_match(['color'], [-1]))
            if GM.is_isomorphic():
                is_upper = False
                for n, d in r[0].nodes_iter(data=True):
                    if d['str_name'].isupper():
                        is_upper = True
                if not is_upper:
                    ret = 1
        return {'subgraph_N' : ret}

    def _get_subgraph_N_X_N(self, graph1, graph2, name1, name2):
        ret = {
            'subgraph_N_0_N' : 0
        }
        # TODO: not worth counting all of them
        # ret = {
        #     'subgraph_N_0_N' : 0,
        #     'subgraph_N_1_N' : 0,
        #     'subgraph_N_2_N' : 0
        # }
        subgraphs1 = self._get_subgraphs(graph1, name1, 2)
        subgraphs2 = self._get_subgraphs(graph2, name2, 2)

        for r in itertools.product(subgraphs1, subgraphs2):
            GM =  nx.algorithms.isomorphism.GraphMatcher(r[0], r[1],
                                                         node_match=iso.categorical_node_match(['str_name'], ['name']),
                                                         edge_match=iso.numerical_edge_match(['color'], [-1]))
            if GM.is_isomorphic():
                for u, v, d in r[0].edges(data=True):
                    if d['color'] == 0:
                        ret['subgraph_N_0_N'] += 1
                        # print u + " " + v + " 0"
                    # TODO: appears to be unuseful
                    # elif d['color'] == 1:
                    #     ret['subgraph_N_1_N'] += 1
                    #     # print u + " " + v + " 1"
                    # elif d['color'] == 2:
                    #     ret['subgraph_N_2_N'] += 1
                    #     # print u + " " + v + " 2"
        return ret

    # TODO: not useful
    def _get_subgraph_3_nodes(self, graph1, graph2, name1, name2):
        ret = {
            'subgraph_3N' : 0
        }
        subgraphs1 = self._get_subgraphs(graph1, name1, 3)
        subgraphs2 = self._get_subgraphs(graph2, name2, 3)

        for r in itertools.product(subgraphs1, subgraphs2):
            GM =  nx.algorithms.isomorphism.GraphMatcher(r[0], r[1],
                                                         node_match=iso.categorical_node_match(['str_name'], ['name']),
                                                         edge_match=iso.numerical_edge_match(['color'], [-1]))
            if GM.is_isomorphic():
                ret['subgraph_3N'] += 1
        return ret

    def _get_subgraphs(self, graph, name, size=3):
        subgraphs = set()
        # print "\nSubgraphs START: " + name
        target = nx.complete_graph(size)
        for sub_nodes in itertools.combinations(graph.nodes(),len(target.nodes())):
            subg = graph.subgraph(sub_nodes)
            if nx.is_weakly_connected(subg):
                # print subg.edges()
                subgraphs.add(subg)
        # print "Subgraphs END \n"
        return subgraphs

def test():
    sf = SimFeatures()
    print sf.get_all_features()

if __name__ == "__main__":
    test()
