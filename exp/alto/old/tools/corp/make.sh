#!/usr/bin/env bash

for dir in $@; do
    fn=$(find $dir -name '*-ud-train.conllu')
    lang=`basename $fn | cut -d'-' -f1`
    echo processing $fn
    outdir=corp/$lang
    mkdir -p $outdir
    python tools/dep_to_isi.py $fn > $outdir/train.graphs
    cat $outdir/train.graphs | python tools/filter_large.py 40 > $outdir//train_nolarge.graphs
    python tools/create_terminals.py $fn > $outdir/train.terminals

done

