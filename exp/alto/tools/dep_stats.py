from __future__ import division, print_function
import sys


def read_stats(fn):
    dep_count_by_lang = {}
    lang_totals = {}
    with open(fn) as f:
        header = f.readline().split()
        if not header[0] == 'lang':
            raise ValueError('first line of dep stat file must be the header!')
        deps = header[1:]
        for line in f:
            fields = line.strip().split()
            lang, counts = fields[0], map(int, fields[1:])
            lang_totals[lang] = sum(counts)
            dep_count_by_lang[lang] = {
                deps[i]: count for i, count in enumerate(counts)}
    return deps, lang_totals, dep_count_by_lang


def main():
    fn = sys.argv[1]
    deps, lang_totals, dep_count_by_lang = read_stats(fn)
    dep_percentage_by_lang = {
        lang: {dep: dep_count_by_lang[lang][dep] / total
               for dep in deps}
        for lang, total in lang_totals.items()}
    totals = {
        dep: sum([dep_count_by_lang[lang][dep]
                  for lang in lang_totals])
        for dep in deps}
    av_percentages = {
        dep: sum([dep_percentage_by_lang[lang][dep]
                  for lang in lang_totals]) / len(lang_totals)
        for dep in deps}

    for dep, av_perc in sorted(av_percentages.items(), key=lambda (d, f): -f):
        top_perc, top_lang = sorted(
                [(dep_percentage_by_lang[lang][dep], lang)
                 for lang in lang_totals])[-1]
        print("{0}\t{1:.2%}\t{2}\t{3:.2%}\t{4}".format(
            dep, av_perc, totals[dep], top_perc, top_lang))


if __name__ == "__main__":
    main()
