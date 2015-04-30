from ConfigParser import ConfigParser
import logging
import re
import sys

import zmq

from longman_parser import XMLParser

class Parser(XMLParser):
    sen_regex = re.compile(
        '<sentence id="[0-9]*">(.*?)</sentence>', re.S)
    basic_deps_regex = re.compile(
        '<dependencies type="collapsed-ccprocessed-dependencies">(.*?)</dependencies>', re.S)  # nopep8
    all_corefs_regex = re.compile(
        '<coreference>(.*)</coreference>', re.S)  # greedy star, has to be
    dep_regex = re.compile(
        '<dep type="(.*?)">.*?\
        <governor idx="([0-9]*)">(.*?)</governor>.*?\
        <dependent idx="([0-9]*)">(.*?)</dependent>', re.S)
    repr_mention_regex = re.compile(
        '<mention representative="true">(.*?)</mention>', re.S)

    @staticmethod
    def parse_mention(mention):
        sen_no = int(Parser.get_section('sentence', mention))
        start_index = int(Parser.get_section('start', mention))
        head_index = int(Parser.get_section('head', mention))
        word = Parser.get_section(
            'text', mention).split()[head_index-start_index]
        return word, sen_no

    @staticmethod
    def parse_corefs(corefs):
        parsed_corefs = []
        for coref in Parser.iter_sections("coreference", corefs):
            repr_mention = Parser.repr_mention_regex.search(coref).group(1)
            mentions = Parser.iter_sections('mention', coref)
            repr_word, sen_no = Parser.parse_mention(repr_mention)
            other_words = map(Parser.parse_mention, mentions)
            parsed_corefs.append(((repr_word, sen_no), other_words))
        return parsed_corefs

    @staticmethod
    def parse_sen(sen):
        deps_string = Parser.basic_deps_regex.search(sen).group(1)
        return [(dep, (word1, id1), (word2, id2))
                for dep, id1, word1, id2, word2 in Parser.dep_regex.findall(
                    deps_string)]

    @staticmethod
    def parse_corenlp_output(output):
        parsed_sens = [Parser.parse_sen(sen)
                       for sen in Parser.sen_regex.findall(output)]

        corefs_match = Parser.all_corefs_regex.search(output)
        if corefs_match is None:
            corefs = []
        else:
            corefs = Parser.parse_corefs(corefs_match.group(1))
        return parsed_sens, corefs

class CoreNLPWrapper():

    def __init__(self, cfg, is_server=False):
        self.cfg = cfg
        zmq_context = zmq.Context()
        self.socket = zmq_context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5900")

    def parse_text(self, text):
        self.socket.send("process {0}".format(text))
        output = self.socket.recv()
        return Parser.parse_corenlp_output(output)

    def parse_sentences(self, sens):
        return self.parse_text("\n".join(sens))

def test():
    cfg_file = 'conf/default.cfg' if len(sys.argv) < 2 else sys.argv[1]
    cfg = ConfigParser()
    cfg.read([cfg_file])

    wrapper = CoreNLPWrapper(cfg)
    parsed_sens, corefs = wrapper.parse_text(
        open('test/input/mrhug_story.sens').read())
    print 'parsed_sens:', parsed_sens
    print 'corefs:', corefs

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")

    test()
