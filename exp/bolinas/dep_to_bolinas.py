#!/usr/bin/env python
# *-* coding=utf-8 *-*

import sys
import re


def get_dep(line):
    return line[0:line.index('(')].replace(":", "_")


def get_dep_words(line):
    x = line[line.index('(')+1:-2]
    word1, word2 = x.split(', ')
    if word1.startswith("ROOT"):
        word1 = "ROOT"
    if word2.startswith("ROOT"):
        word2 = "ROOT"
    return word1, word2


def dep_to_dict(fn):
    all_sens = []
    sentence_dict = {}
    for line in open(fn, "r"):
        if re.search("^\(ROOT", line):
            if sentence_dict != {}:
                all_sens.append(sentence_dict)
                sentence_dict = {}
        if re.search("^[a-zA-Z]", line):
            dep = get_dep(line)
            words = get_dep_words(line)
            if words[0] not in sentence_dict:
                sentence_dict[words[0]] = {}
            if words[1] not in sentence_dict:
                # make sure all words are in the dictionary
                sentence_dict[words[1]] = {}
            sentence_dict[words[0]][words[1]] = dep

    if sentence_dict != {}:
        all_sens.append(sentence_dict)
        sentence_dict = {}

    return all_sens


def dict_to_graph(dictionary, node):
    # print dictionary
    global SEEN
    global GRAPH_STRING
    if node in SEEN:
        GRAPH_STRING += node + '.'
    else:
        GRAPH_STRING += "({0}. :{1}".format(node, node.split('-')[0])
        for neighbor in dictionary[node]:
            edge = dictionary[node][neighbor]
            GRAPH_STRING += ' ' + ':' + edge + ' '
            dict_to_graph(dictionary, neighbor)
        GRAPH_STRING += ')'


def main():
    sentence_dicts = dep_to_dict(sys.argv[1])
    global SEEN
    global GRAPH_STRING
    for sentence_dict in sentence_dicts:
        SEEN = {}
        GRAPH_STRING = ''
        dict_to_graph(sentence_dict, 'ROOT')
        print GRAPH_STRING


if __name__ == "__main__":
    main()
