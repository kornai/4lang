#!/usr/bin/env bash
for file in data/longman.dep.newest/*; do basename $file | cut -d'.' -f1 | tr '\n' '\t'; grep 'ROOT' $file; done | sed 's/root(ROOT-0, \(.*\)-[0-9]*)/\1/g' > data/longman.hypernyms
