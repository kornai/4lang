#!/bin/bash

CONLLU_FILE="${1}"
python create_terminals.py "${CONLLU_FILE}" | cat ../ud/en_ud_bi.irtg ../ud/ud_dumb_preterms_bi -
