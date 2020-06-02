## Usage of the grammars
1. First download the alto parser in this directory
   1. For that, run `alto.sh`
2. Two simple grammars are provided for example
   1. `simple_4lang.irtg` that maps between `fourlang` and `equation` interpretations
      1. simple input is provided in the `simple_4lang_input_example` file
   2. `svo2sov.irtg` that changes word order with the interpretations `svo` and `sov`
      1. simple input is provided in the `svo2sov_simple_example` file
3. Alto can be run with the command
  
   ```bash
   java -Xmx8G -cp alto-2.3.6-SNAPSHOT-all.jar de.up.ling.irtg.script.ParsingEvaluator simple_4lang_input_example -g simple_4lang.irtg -I fourlang -O equation=toString -o surface_eval_ewt
   ```
   * Where `simple_4lang_input_example` is the input file, `-g simple_4lang.irtg` is the grammar file  `-I fourlang -O equation=toString ` is the input and the output interpretations and `-o surface_eval_ewt` is the output file, where the result will be stored. The command for the `svo2sov.irtg` would look like:
  
  ```bash
    java -Xmx8G -cp alto-2.3.6-SNAPSHOT-all.jar de.up.ling.irtg.script.ParsingEvaluator svo2sov_simple_example -g svo2sov.irtg -I svo -O sov=toString -o surface_eval_ewt
  ```


  ***Please note that every input file requires atleast 2 input, that is the reason there is a dummy line in every example input***