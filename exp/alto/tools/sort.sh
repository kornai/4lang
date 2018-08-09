#!/bin/bash

NPS="${1}"
TMP_ORDERED="/tmp/tmp_ordered"
TMP_ORDERED2="/tmp/tmp_ordered2"
TMP_ORDERED3="/tmp/tmp_ordered3"


# Sort input file in alphabetical order
cat "${NPS}"  | sort > "${TMP_ORDERED}"
# width
python sort_nps2.py "${TMP_ORDERED}" | sort -n -s | cut -d" " -f2- > "${TMP_ORDERED2}"
# depth
python sort_nps.py "${TMP_ORDERED2}" | sort -n -s | cut -d" " -f2- > "${TMP_ORDERED3}"

# Get rid of identical lines
python3 line_filter.py "${TMP_ORDERED3}"

# Remove temporary files
rm "${TMP_ORDERED}"
rm "${TMP_ORDERED2}"
rm "${TMP_ORDERED3}"