# creates word lists in each languages of 4lang and uroboros words
# encoded in utf8
# replaces _ with space
# discards unknown fields

awk 'BEGIN {FS="\t";OFS="\t"} {print $5, $1}' 4lang.urob | sed 's/_/ /g' | tee tmp_en | cut -f2 -d $'\t' | sort -u > 4lang.en
awk 'BEGIN {FS="\t";OFS="\t"} {print $5, $2}' 4lang.urob | ./p2iso | iconv -f latin2 -t utf8 | tee tmp_hu | cut -f2 | sed 's/_/ /g' | grep "#" -v | grep -v "N/A" | sort -u > 4lang.hu
awk 'BEGIN {FS="\t";OFS="\t"} {print $5, $3}' 4lang.urob | tee tmp_la | cut -f2 | sed 's/_/ /g' | grep "#" -v | grep -v "N/A" | sort -u > 4lang.la
awk 'BEGIN {FS="\t";OFS="\t"} {print $5, $4}' 4lang.urob | perl polish_p2utf8 | tee tmp_pl | cut -f2 | sed 's/_/ /g' | grep "#" -v | grep -v "N/A" | sort -u > 4lang.pl

paste -d $'\t' <(paste -d $'\t' tmp_en tmp_hu) <(paste -d $'\t' tmp_la tmp_pl) | awk 'BEGIN {FS="\t";OFS="\t"} {print $1,$2,$4,$6,$8}' | sort -n > 4lang.table

rm tmp_en tmp_hu tmp_la tmp_pl

awk 'BEGIN {FS="\t";OFS="\t"} {if ($6 == "u") print $1}' 4lang.urob | sed 's/_/ /g' | uniq > uroboros.en
awk 'BEGIN {FS="\t";OFS="\t"} {if ($6 == "u") print $2}' 4lang.urob | ./p2iso | iconv -f latin2 -t utf8 | sed 's/_/ /g' | grep "#" -v | grep -v "N/A" | uniq > uroboros.hu
awk 'BEGIN {FS="\t";OFS="\t"} {if ($6 == "u") print $3}' 4lang.urob | sed 's/_/ /g' | grep "#" -v | grep -v "N/A" | uniq > uroboros.la
awk 'BEGIN {FS="\t";OFS="\t"} {if ($6 == "u") print $4}' 4lang.urob | perl polish_p2utf8 | sed 's/_/ /g' | grep "#" -v | grep -v "N/A" | uniq > uroboros.pl

awk 'BEGIN {FS="\t";OFS="\t"} {if ($6 == "u") print $5}' 4lang.urob > uroboros.ids
