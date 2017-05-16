#!/usr/bin/env bash

for dir in $@; do
    lang=`basename $dir`
    echo processing $lang
    fn=$(find $dir -name '*nolarge.graphs')
    terminals=$(find $dir -name '*terminals')
    grammar=$dir/grammar_with_terminals.irtg
    cat ud/ud.irtg $terminals > $grammar
    echo created $grammar
    outdir=output/$lang
    logdir=log/$lang
    mkdir -p $outdir $logdir
    sem -j8 nice java -cp /home/recski/projects/alto/target/alto-2.2-SNAPSHOT-jar-with-dependencies.jar de.up.ling.irtg.script.ParsingEvaluator $fn -g $grammar -I graph -o $outdir/output 2> $logdir/log &
done

