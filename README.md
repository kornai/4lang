## 4lang
Concept dictionary using Eilenberg machines

## Dict-to-4lang
A pipeline that processes entries in monolingual dictionaries builds 4lang-style definitions for each headword
Currently only the preprocessing is performed by this module, the actual machines are created by the [pymachine](https://github.com/kornai/pymachine) module

To process the Longman Dictionary of Contemporary English (LDOCE).
This command will build a using
  `python src/dict_to_4lang.py conf/longman_firsts.cfg n`

where n is the number of threads to be used and the config file contains the location of input and output files. The file `conf/default.cfg` should contain the path to an installation of the [Stanford Dependency Parser](http://nlp.stanford.edu/software/lex-parser.shtml#Download)
