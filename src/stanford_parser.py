import json
import math
import os
import sys
from tempfile import NamedTemporaryFile

sys.path.append(sys.argv[1])

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

    def parse_with_constraints(self, sentence, constraints):
        query = self.lp.parserQuery()
        query.setConstraints(constraints)
        query.parse(self.tokenize(sentence))
        parse = query.getBestParse()
        gs = self.get_grammatical_structure(parse)
        dependencies = gs.typedDependenciesCollapsed()
        return parse, gs, dependencies

    def parse_definitions(self, in_file, out_file):
        with open(in_file) as in_obj:
            entries = json.load(in_obj)
        with NamedTemporaryFile(dir="/tmp", delete=False) as log_file:
            for c, entry in enumerate(entries):
                if c % 100 == 0:
                    log_file.write("parsed {0} entries\n".format(c))
                    log_file.flush()
                pos = entry['pos']
                for sense in entry['senses']:
                    sentence = sense['definition']
                    if sentence is None:
                        continue
                    constraints = StanfordParser.get_constraints(sentence, pos)
                    parse, _, dependencies = self.parse_with_constraints(
                        sentence, constraints)

                    dep_strings = map(unicode, dependencies)
                    sense['definition'] = {
                        'sen': sentence,
                        'deps': dep_strings}

        with open(out_file, 'w') as out:
            json.dump(entries, out)

def test():
    parser = StanfordParser(sys.argv[2])

    sentence = 'the size of a radio wave used to broadcast a radio signal'
    pos = 'n'
    parse, _, dependencies = parser.parse_with_constraints(
        sentence, StanfordParser.get_constraints(sentence, pos))

    print parse.pennPrint()
    print "\n".join(map(str, dependencies))

def main():
    parser_file, in_file, out_file = sys.argv[2:5]
    parser = StanfordParser(parser_file)
    parser.parse_definitions(in_file, out_file)

if __name__ == "__main__":
    main()
