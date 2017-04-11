#!/usr/bin/env bash
grep -v '^#' | grep -v '^$' | grep '^_null_$' -v | tr '(' '\n' | tr -s ')' '\n' | tr -d ','  | grep '^_' | sort | uniq -c | sort -nr
