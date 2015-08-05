import json
import logging
import math
import os
import sys
from tempfile import NamedTemporaryFile

parser = sys.argv[1]
sys.path.append(parser)
sys.path.append(os.path.join(os.path.dirname(parser), 'ejml-0.23.jar'))

from edu.stanford.nlp.process import Morphology, PTBTokenizer, WordTokenFactory
from edu.stanford.nlp.parser.common import ParserConstraint
from edu.stanford.nlp.parser.lexparser import Options
from edu.stanford.nlp.parser.lexparser import LexicalizedParser
from edu.stanford.nlp.ling import Sentence
from edu.stanford.nlp.trees import PennTreebankLanguagePack

from java.io import StringReader
from java.util.regex import Pattern

class StanfordParser:

    @staticmethod
    def get_constraints(sentence, pos):
        constraints = []
        length = len(sentence)
        if pos == 'n':
            constraints.append(
                ParserConstraint(0, length, Pattern.compile("NP.*")))
        return constraints

    def __init__(self, parser_file,
                 parser_options=['-maxLength', '80',
                                 '-retainTmpSubcategories']):

        """@param parser_file: path to the serialised parser model
            (e.g. englishPCFG.ser.gz)
        @param parser_options: options
        """

        assert os.path.exists(parser_file)
        options = Options()
        options.setOptions(parser_options)
        self.lp = LexicalizedParser.getParserFromFile(parser_file, options)
        tlp = PennTreebankLanguagePack()
        self.gsf = tlp.grammaticalStructureFactory()
        self.lemmer = Morphology()
        self.word_token_factory = WordTokenFactory()
        self.parser_query = None

    def tokenize(self, text):
        reader = StringReader(text)
        tokeniser = PTBTokenizer(reader, self.word_token_factory, None)
        tokens = tokeniser.tokenize()
        return tokens

    def get_parse(self, sentence):
        tokens = [unicode(x) for x in self.tokenize(sentence)]
        parse = self.lp.apply(Sentence.toWordList(tokens))
        return parse

    def get_grammatical_structure(self, parse):
        return self.gsf.newGrammaticalStructure(parse)

    def get_kbest(self, query, k=3):
        for candidate_tree in query.getKBestPCFGParses(k):
            parse = candidate_tree.object()
            prob = math.e ** candidate_tree.score()
            yield prob, parse

    def parse(self, sentence):
        return self.parse_with_constraints(sentence, None)

    def parse_with_constraints(self, sentence, constraints):
        # logging.debug("getting query...")
        query = self.lp.parserQuery()
        if constraints is not None:
            query.setConstraints(constraints)
        # logging.debug("tokenizing...")
        toks = self.tokenize(sentence)
        # logging.debug("running parse...")
        query.parse(toks)
        # logging.debug("getting best...")
        parse = query.getBestParse()
        # logging.debug("getting gs...")
        gs = self.get_grammatical_structure(parse)
        # dependencies = gs.typedDependenciesCollapsed()
        dependencies = gs.typedDependenciesCCprocessed()
        return parse, gs, dependencies

    def parse_sens(self, in_file, out_file, log=False):
        logging.debug("reading input...")
        with open(in_file) as in_obj:
            sens = json.load(in_obj)
        parsed_sens = []
        if log:
            log_file = NamedTemporaryFile(dir="/tmp", delete=False)
        for c, sentence in enumerate(sens):
            if log and c % 100 == 0:
                log_file.write("parsed {0} sentences\n".format(c))
                log_file.flush()
            parse, _, dependencies = self.parse(sentence)

            dep_strings = map(unicode, dependencies)
            parsed_sens.append({
                'sen': sentence,
                'deps': dep_strings})

        with open(out_file, 'w') as out:
            json.dump(parsed_sens, out)

    def parse_definitions(self, in_file, out_file):
        with open(in_file) as in_obj:
            entries = json.load(in_obj)
        with NamedTemporaryFile(dir="/tmp", delete=False) as log_file:
            for c, entry in enumerate(entries):
                if c % 100 == 0:
                    log_file.write("parsed {0} entries\n".format(c))
                    log_file.flush()
                for sense in entry['senses']:
                    sentence = sense['definition']
                    if sentence is None:
                        continue
                    # sentence += '.'  # fixes some parses and ruins others
                    pos = sense['pos']
                    constraints = StanfordParser.get_constraints(sentence, pos)
                    # logging.info('sen: {0}, constraints: {1}'.format(
                    #    sentence, constraints))
                    try:
                        parse, _, dependencies = self.parse_with_constraints(
                            sentence, constraints)
                    except:
                        sys.stderr.write(
                            u'parse failed on sentence: {0}'.format(
                                sentence).encode('utf-8'))
                        dep_strings = []
                    else:
                        dep_strings = map(unicode, dependencies)

                    sense['definition'] = {
                        'sen': sentence,
                        'deps': dep_strings}

        with open(out_file, 'w') as out:
            json.dump(entries, out)

def test():
    logging.warning("running test, not main!")
    parser = StanfordParser(sys.argv[2])

    # dv_model = parser.lp.reranker.getModel()
    # print dv_model

    # sentence = 'the size of a radio wave used to broadcast a radio signal'
    sentence = 'a man whose job is to persuade people to buy his company\'s \
        products.'
    pos = 'n'
    parse, gs, dependencies = parser.parse_with_constraints(
        sentence, StanfordParser.get_constraints(sentence, pos))

    print type(parse), type(gs)
    print parse.pennPrint()
    print "\n".join(map(str, dependencies))

def main():
    parser_file, in_file, out_file, is_defs, loglevel = sys.argv[2:7]
    logging.basicConfig(
        level=int(loglevel),
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    logging.debug("initializing parser...")
    parser = StanfordParser(parser_file)
    if int(is_defs):
        parser.parse_definitions(in_file, out_file)
    else:
        parser.parse_sens(in_file, out_file)

if __name__ == "__main__":
    main()
    # test()
