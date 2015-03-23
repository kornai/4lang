from ConfigParser import ConfigParser
import logging
import re
import subprocess
import sys
from tempfile import NamedTemporaryFile

from longman_parser import XMLParser
from utils import ensure_dir

class Parser(XMLParser):
    sen_regex = re.compile(
        '<sentence id="[0-9]*">(.*?)</sentence>', re.S)
    basic_deps_regex = re.compile(
        '<dependencies type="basic-dependencies">(.*?)</dependencies>', re.S)
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
    def parse_all(stream):
        output = stream.read()  # TODO
        parsed_sens = [Parser.parse_sen(sen)
                       for sen in Parser.sen_regex.findall(output)]
        corefs = Parser.parse_corefs(
            Parser.all_corefs_regex.search(output).group(1))
        return parsed_sens, corefs

class CoreNLPWrapper():

    def __init__(self, cfg, is_server=False):
        self.cfg = cfg
        self.get_paths()

    def get_paths(self):
        self.class_name = self.cfg.get('corenlp', 'class_name')
        self.classpath = self.cfg.get('corenlp', 'classpath')
        self.tmp_dir = self.cfg.get('data', 'tmp_dir')
        ensure_dir(self.tmp_dir)

    def run_parser(self, in_file_name):
        return_code = subprocess.call([
            'java', '-cp', self.classpath, '-Xmx2g',
            self.class_name, '-file', in_file_name])

        return return_code == 0

    def parse_sentences(self, sens, definitions=False):
        logging.debug("dumping input...")
        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as in_file:
            in_file.write('\n'.join(sens))
            in_file_name = in_file.name

        logging.debug("running parser...")
        assert self.run_parser(in_file_name)

        logging.debug("reading output...")
        out_file_name = "{0}.xml".format(in_file_name.split('/')[-1])
        with open(out_file_name) as out_file:
            parsed_sens, corefs = Parser.parse_all(out_file)

        return parsed_sens, corefs

def test():
    cfg_file = 'conf/default.cfg' if len(sys.argv) < 2 else sys.argv[1]
    cfg = ConfigParser()
    cfg.read([cfg_file])

    wrapper = CoreNLPWrapper(cfg)
    parsed_sens, corefs = wrapper.parse_sentences(
        [line.strip() for line in open('data/mrhug_story.sens').readlines()])
    print 'parsed_sens:', parsed_sens
    print 'corefs:', corefs

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")

    test()
