## 4lang

This repository provides
    - the `4lang` concept dictionary, which contains manually written concept definitions
    - the `text_to_4lang` module, which creates concept graph representations from running text
    - the `dict_to_4lang` module, which builds more of these definitions from human-readable dictionaries


### Dependencies

#### pymachine
Our tools require an installation of the [pymachine](http://github.com/kornai/pymachine) implementation of Eilenberg-machines (just clone it to your machine and run `python setup.py install`).

#### hunmorph
For lemmatization, `4lang` uses the `hunmorph` tool, on most UNIX-based systems you can use [these pre-compiled executables and models](http://people.mokk.bme.hu/~recski/4lang/huntools_binaries.tgz) (just extract them in your `4lang` directory). If they don't work on your system, you may have to download and recompile `hunmorph` and/or the model it uses following the instructions [here](http://mokk.bme.hu/en/resources/hunmorph/). This process is quite error-prone, but please [reach out](#Contact) to us and we'll be happy to help you!

__NOTE__: All remaining dependencies are required only for building 4lang graphs, so in case you only want to use the graphs we provide (e.g. for the machine similarity component of our [Semeval STS system](https://github.com/juditacs/semeval/)), you can skip the rest of this section and continue to [download pre-compiled graphs](#Downloading-pre-compiled-graphs).

#### Stanford Parser, CoreNLP, jython
For parsing dictionary definitions, `4lang` requires the [Stanford Dependency Parser](http://nlp.stanford.edu/software/lex-parser.shtml#Download). Additionally, `text_to_4lang.py` requires the [Stanford CoreNLP](http://nlp.stanford.edu/software/corenlp.shtml#Download) toolkit for parsing and coreference resolution, while the `dict_to_4lang` tool requires [jython](http://www.jython.org/downloads.html) for customized parsing via the Stanford Parser API. Both tools require a copy of the RNN-based parser model for English, which is distributed alongside the Stanford Parser.

After downloading and installing these tools, all you need to do is edit the `stanford` and `corenlp` sections of the configuration file used to run the `4lang` tools so that the relevant fields point to your installations of each tool and your copy of the englishRNN.ser.gz model (more on config files below).

### Downloading pre-compiled graphs
We provide [serialized machine graphs](http://people.mokk.bme.hu/~recski/4lang/machines.tgz) built from `4lang` definitions as well as from the English Wiktionary (using the `dict_to_4lang` module). Unpacking this archive in your `4lang` directory will place them in the `data/machines` directory, which is the default location for compiled machine graphs.

### Usage

#### Semeval STS
To use `4lang` from our [Semeval STS system](https://github.com/juditacs/semeval/) you just need to edit the `4langpath` and `hunmorph_path` attributes in your semeval config file so that they point to your 4lang directory and the downloaded `hunmorph` binaries, respectively.

#### Dict_to_4lang and Text_to_4lang

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
