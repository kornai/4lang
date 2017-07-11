for dir in ../input/ud/ud-treebanks-v2.0/UD*; do
    prefix=`basename $dir`
    echo $prefix
    fn=$dir/*-train.conllu
    python tools/dep_to_isi.py $fn > $dir/${prefix}_train.graphs
    cat $dir/${prefix}_train.graphs | python tools/filter_large.py 25 > $dir/${prefix}_train_max25.graphs

done
