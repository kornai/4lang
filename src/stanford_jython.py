import sys



sys.path.append(sys.argv[1])
 
from java.io import CharArrayReader
from edu.stanford.nlp import *
 
lp = parser.lexparser.LexicalizedParser('edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')
tlp = trees.PennTreebankLanguagePack()
lp.setOptionFlags(["-maxLength", "80", "-retainTmpSubcategories"])
 
sentence = 'One of my favorite features of functional programming \
languages is that you can treat functions like values.'
 
toke = tlp.getTokenizerFactory().getTokenizer(CharArrayReader(sentence));
wordlist = toke.tokenize()
 
if (lp.parse(wordlist)):
    parse = lp.getBestParse()
 
gsf = tlp.grammaticalStructureFactory()
gs = gsf.newGrammaticalStructure(parse)
tdl = gs.typedDependenciesCollapsed()
 
print parse.toString() 
print tdl
