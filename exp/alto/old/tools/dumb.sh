for dir in ../input/ud/ud-treebanks-v2.0/UD*; do
    prefix=`basename $dir`
    echo $prefix
    mkdir -p ../ud/langspec/$prefix
    fn=$dir/*-train.conllu
    python create_terminals.py $fn > ../ud/langspec/$prefix/$prefix.terminals
    cat ../ud/ud_dumb.irtg ../ud/ud_dumb_preterms ../ud/langspec/$prefix/$prefix.terminals > ../ud/langspec/$prefix/$prefix.irtg
done
