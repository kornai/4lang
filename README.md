## 4lang

This repository provides
    - the `4lang` concept dictionary, which contains manually written concept definitions
    - the `text_to_4lang` module, which creates concept graph representations from running text
    - the `dict_to_4lang` module, which builds more of these definitions from human-readable dictionaries


### Dependencies

Our tools require an installation of the [pymachine](http://github.com/kornai/pymachine) implementation of Eilenberg-machines (just clone it to your machine and run `python setup.py install`). All other dependencies are for building 4lang graphs, so in case you only want to use the graphs we provide (e.g. to provide the machine similarity component of our [Semeval STS system](https://github.com/juditacs/semeval/)), you can skip the rest of this section and continue to [download pre-compiled graphs](#Downloading-pre-compiled-graphs).

For parsing dictionary definitions, `4lang` requires the [Stanford Dependency Parser](http://nlp.stanford.edu/software/lex-parser.shtml#Download). Additionally, `text_to_4lang.py` requires the [Stanford CoreNLP](http://nlp.stanford.edu/software/corenlp.shtml#Download) toolkit for parsing and coreference resolution, while the `dict_to_4lang` tool requires [jython](http://www.jython.org/downloads.html) for customized parsing via the Stanford Parser API. Both tools require a copy of the RNN-based parser model for English, which is distributed alongside the Stanford Parser.

After downloading and installing these tools, all you need to do is edit the `stanford` and `corenlp` sections of the configuration file used to run the `4lang` tools so that the relevant fields point to your installations of each tool and your copy of the englishRNN.ser.gz model (more on config files below).

### Downloading pre-compiled graphs

### Usage

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
