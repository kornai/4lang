import math
import os
import sys

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

def main():
    parser_file = sys.argv[2]
    parser = StanfordParser(parser_file)

    query = parser.lp.parserQuery()
    #constraints = [ParserConstraint(0, 3, Pattern.compile("VP.*"))]
    constraints = [ParserConstraint(0, 12, Pattern.compile("NP.*"))]
    query.setConstraints(constraints)

    sentence = 'the size of a radio wave used to broadcast a radio signal'

    toks = parser.tokenize(sentence)
    query.parse(toks)
    parse = query.getBestParse()

    gs = parser.get_grammatical_structure(parse)
    dependencies = gs.typedDependenciesCollapsed()

    print parse.pennPrint()
    print "\n".join(map(str, dependencies))

if __name__ == "__main__":
    main()
