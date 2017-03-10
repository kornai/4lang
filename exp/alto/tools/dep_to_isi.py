#!/usr/bin/env python
from collections import defaultdict
import sys

from hunmisc.corpustools.tsv_tools import sentence_iterator, get_dependencies

from common import sanitize_word


def get_node_id_and_word(token):
    word, i = token
    word = sanitize_word(word)
    node_id = "{0}_{1}".format(word, i)
    return node_id, word


def deps_to_sen_dict(deps):
    root_token = None
    sen_dict = defaultdict(dict)
    for dep in deps:
        gov = (dep['gov']['word'], dep['gov']['id'])
        ddep = (dep['dep']['word'], dep['dep']['id'])
        dtype = dep['type']
        sen_dict[gov][ddep] = dtype
        if dtype == 'root':
            root_token = gov

    return sen_dict, root_token


def dict_to_graph(sen_dict, token):
    # print dictionary
    global SEEN
    global GRAPH_STRING
    if token in SEEN:
        node_id = SEEN[token]
        GRAPH_STRING += node_id
    else:
        node_id, word = get_node_id_and_word(token)
        SEEN[token] = node_id
        GRAPH_STRING += "({0} / {0}".format(node_id, word)
        for neighbor, edge in sen_dict[token].iteritems():
            GRAPH_STRING += ' :{0} '.format(edge)
            dict_to_graph(sen_dict, neighbor)
        GRAPH_STRING += ')'


HEADER = (
    '# IRTG unannotated corpus file, v1.0\n' +
    '# interpretation graph: de.up.ling.irtg.algebra.graph.GraphAlgebra')


def main():
    print(HEADER)
    id_field, word_field, lemma_field, msd_field, gov_field, dep_field = (
            0, 1, None, None, -4, -3)
    global SEEN
    global GRAPH_STRING
    with open(sys.argv[1]) as stream:
        for sentence in sentence_iterator(stream, comment_tag='#'):
            deps = get_dependencies(
                sentence, id_field, word_field, lemma_field, msd_field,
                gov_field, dep_field)

            sentence_dict, root_token = deps_to_sen_dict(deps)
            # root token will be the first token if ROOT doesn't exist
            if root_token is None:
                root_token = sentence_dict.keys()[0]
            SEEN = {}
            GRAPH_STRING = ''
            dict_to_graph(sentence_dict, root_token)
            print(GRAPH_STRING)


if __name__ == "__main__":
    main()
