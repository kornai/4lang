#!/usr/bin/env bash

# https://stackoverflow.com/questions/6593531/running-a-limited-number-of-child-processes-in-parallel-in-bash/14387296#14387296
function maxn {
   while [ `jobs | wc -l` -ge 3 ]
   do
      sleep 5
   done
}



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
    echo parsing ${fn}...
    maxn; time nice java -cp /home/recski/projects/alto/target/alto-2.2-SNAPSHOT-jar-with-dependencies.jar de.up.ling.irtg.script.ParsingEvaluator $fn -g $grammar -I graph -o $outdir/output 2> $logdir/log &
    #echo done!
done

