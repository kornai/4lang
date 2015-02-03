#!/usr/bin/env bash
for file in data/longman.sen/*; do
    word=`basename $file | cut -d'.' -f1`
    echo $word
    $STANFORD_PARSER/lexparser_dep.sh $file > data/longman.dep/$n.dep
done
