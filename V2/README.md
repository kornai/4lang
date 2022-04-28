# The parser

```
usage: def_ply_parser.py [-h] -i INPUT_FILE -o OUTPUT_DIR [-f {4lang,def,column}] [-c CLAUSE]

def_ply_parser.py -i <inputfile> -o <outputdir> -f <format> -c <clause>

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        The input file, should be a tsv
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        The output directory, where the processed files will be stored
  -f {4lang,def,column}, --format {4lang,def,column}
                        Choose the process mode. 4lang expects the full column list, def only excpets a single column with the definitions, column expects 2 columns: the words
                        itself and the definitions
  -c CLAUSE, --clause CLAUSE
                        The clause you want to filter the definitions with
```

## Dependencies

You need to install the _ply_ parser:
```
pip install ply
```
 
## Usage

To simply parse the _700.tsv_ file just run:
```
python def_ply_parser.py -i 700.tsv -o output
```

The _output_ folder will contain all the processed files. The files are the following:
- __4lang_def_correct__: will contain all the correct lines
- __4lang_def_correct_filtered__: if --clause is provided, the file will contain lines filtered by that clause
- __4lang_def_correct_substituted__: contains the substituted definitions
- __4lang_def_correct_substituted_top_level__: contains top level definitions, one by a line
- __4lang_def_errors__: contains the lines with parser errors
- __top_level_clauses__: prints out the top level clauses

The __4lang_def_correct_substituted_top_level__ file will contain only the splitted definitions. You can also use the parser to parse this file:
```
python def_ply_parser.py -i output/4lang_def_correct_substituted_top_level -o output -f def
```
