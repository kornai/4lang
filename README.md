## 4lang

This repository provides
- the `4lang` concept dictionary, which contains manually written concept
  definitions. (Learn more about the filelds of the tsv file [here](https://github.com/kornai/4lang/wiki/Fields-in-the-concept-dictionary))
- the `text_to_4lang` module, which creates concept graph representations from running text
- the `dict_to_4lang` module, which builds more of these definitions from human-readable dictionaries


### Dependencies

#### pymachine
Our tools require an installation of the [pymachine](http://github.com/kornai/pymachine) implementation of Eilenberg-machines.

#### hunmorph
For lemmatization, `4lang` uses the `hunmorph` tool, on most UNIX-based systems you can use [these pre-compiled executables and models](http://people.mokk.bme.hu/~recski/4lang/huntools_binaries.tgz) (just extract them in your `4lang` directory). On 64-bit systems you may have to install the `libc6-i386` package for the `hundisambig` binary to work.

__NOTE__: All remaining dependencies are required only for building 4lang graphs, so in case you only want to use the graphs we provide (e.g. for the machine similarity component of our [Semeval STS system](https://github.com/juditacs/semeval/)), you can skip the rest of this section and continue to [download pre-compiled graphs](#downloading-pre-compiled-graphs).

#### Stanford Parser, CoreNLP, jython
For parsing dictionary definitions, `4lang` requires the [Stanford Dependency Parser](http://nlp.stanford.edu/software/lex-parser.shtml#Download). Additionally, `text_to_4lang.py` requires the [Stanford CoreNLP](http://nlp.stanford.edu/software/corenlp.shtml#Download) toolkit for parsing and coreference resolution, while the `dict_to_4lang` tool requires [jython](http://www.jython.org/downloads.html) for customized parsing via the Stanford Parser API. Both tools require a copy of the RNN-based parser model for English, which is distributed alongside the Stanford Parser.

Currently, `text_to_4lang` requires the installation of the [corenlp-server](https://github.com/kowey/corenlp-server) package. Just download the repository and follow the instructions in its README to build the package and start the server (mvn package; mvn exec:java -D server), the text_to_4lang module will then be able to connect.

After downloading and installing these tools, all you need to do is edit the `stanford` and `corenlp` sections of the default configuration file `conf/default.cfg` so that the relevant fields point to your installations of each tool and your copy of the englishRNN.ser.gz model (more on config files below).

### Downloading pre-compiled graphs
We provide [serialized machine graphs](http://sandbox.hlt.bme.hu/~recski/4lang/machines.tgz) built from `4lang` definitions as well as from the English Wiktionary (using the `dict_to_4lang` module). Unpacking this archive in your `4lang` directory will place them in the `data/machines` directory, which is the default location for compiled machine graphs.

### Environment variables
The location of your installations of the above third-party tools, as well as 4lang must be specified via environment variables. These variables must always be set, there are no fallback values to avoid strange bugs. Here's an example of a `bashrc` file setting all required variables:

```
export FOURLANGPATH=/home/recski/projects/4lang
export JYTHONPATH=/home/recski/projects/jython/jython/bin/jython
export STANFORDPATH=/home/recski/projects/stanford_dp
export MAGYARLANCPATH=/home/recski/projects/4lang/magyarlanc
export HUNTOOLSBINPATH=/home/recski/sandbox/huntools_binaries
```

Note that the `JYTHONPATH` variable must point to the jython binary directly (and not a directory), since various jython installations may have different directory structures.

### Usage

#### Semeval STS
To use `4lang` from our [Semeval STS system](https://github.com/juditacs/semeval/) you just need to edit the `4langpath` and `hunmorph_path` attributes in your semeval config file so that they point to your 4lang directory and the downloaded `hunmorph` binaries, respectively.

#### Dict_to_4lang and Text_to_4lang

To run each module on small test datasets, simply run

```
python src/dict_to_4lang.py
python src/text_to_4lang.py
```

Both tools can be configured by editing a copy of [conf/default.cfg](conf/default.cfg) and running

```
python src/dict_to_4lang.py MY_CONFIG_FILE
```
to build `4lang`-style definitions from a monolingual dictionary such as Wiktionary or Longman

```
cat INPUT_FILE | python src/text_to_4lang.py MY_CONFIG_FILE
```
to create concept graphs from running English text


### The config file

### Contact
This repository is maintained by Gábor Recski. Questions, suggestions, bug reports, etc. are very welcome and can be sent by email to recski at aut bme hu.

### Publications
If you use the `4lang` module, please cite:

```
@inproceedings{Kornai:2015a,
    author    = {Kornai, Andr\'as  and  \'{A}cs, Judit  and  Makrai, M\'{a}rton  and  Nemeskey, D\'{a}vid M\'{a}rk  and  Pajkossy, Katalin  and  Recski, G\'{a}bor},
    title     = {Competence in lexical semantics},
    booktitle = {Proceedings of the Fourth Joint Conference on Lexical and Computational Semantics},
    month     = {June},
    year      = {2015},
    address   = {Denver, Colorado},
    publisher = {Association for Computational Linguistics},
    pages     = {165--175},
    url       = {ht
```
