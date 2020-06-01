#!/bin/bash

CONLLU_FILE="${1}"
TMP_PRETERM_FILE="/tmp/tmp_preterm"

# Create temporary preterms file
grep -v "^#" "${CONLLU_FILE}" | grep -v "^$" |
  cut -f4 | sort -u | python dumb_preterms_bi.py > "${TMP_PRETERM_FILE}"
python create_terminals_bi.py "${CONLLU_FILE}" | cat ../ud/en_ud_bi.irtg "${TMP_PRETERM_FILE}" -

# Remove temporary preterms file
rm "${TMP_PRETERM_FILE}"

