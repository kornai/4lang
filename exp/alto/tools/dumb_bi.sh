for dir in ../input/ud/ud-treebanks-v2.0/UD*; do
    prefix=`basename $dir`
    echo $prefix
    mkdir -p ../ud/langspec/$prefix
    fn=$dir/*-train.conllu
    python create_terminals_bi.py $fn > ../ud/langspec/$prefix/$prefix.bi_terminals
    cat ../ud/ud_dumb_bi.irtg ../ud/ud_dumb_preterms_bi ../ud/langspec/$prefix/$prefix.bi_terminals > ../ud/langspec/$prefix/$prefix.bi.irtg
done
