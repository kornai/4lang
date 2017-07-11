ALTO_PATH=/home/recski/projects/alto/target/alto-2.2-SNAPSHOT-jar-with-dependencies.jar
PARSER_CLASS=de.up.ling.irtg.script.ParsingEvaluator

for dir in ../input/ud/ud-treebanks-v2.0/UD*; do
    prefix=`basename $dir`
    echo $prefix
    out_dir=../output/$prefix
    mkdir -p $out_dir
    input_fn=$dir/${prefix}_train_max25.graphs
    grammar_fn=../ud/langspec/$prefix/$prefix.irtg
    out_fn=$out_dir/${prefix}_train_max25.parsed
    log_fn=$out_dir/${prefix}_train_max25.log
    java -Xmx24G -cp $ALTO_PATH $PARSER_CLASS $input_fn -g $grammar_fn -I graph -o $out_fn 2> $log_fn

done
