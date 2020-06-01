from collections import defaultdict
import os
import re
import sys


dep_freq_pattern = re.compile('dep name="(.*)">([0-9]*)<')


def main():
    top_dir = sys.argv[1]
    dirs = os.listdir(top_dir)
    stats_by_lang = defaultdict(lambda: defaultdict(int))
    all_deps = set()
    for dirname in dirs:
        lang = dirname.replace("UD_", "")
        fn = os.path.join(top_dir, dirname, 'stats.xml')
        with open(fn) as f:
            for line in f:
                if 'dep name' in line:
                    dep, freq = dep_freq_pattern.search(line).groups()
                    all_deps.add(dep)
                    stats_by_lang[lang][dep] = freq

    sorted_deps = sorted(list(all_deps))
    header = "\t".join(["lang"] + sorted_deps)
    print(header)
    for lang in sorted(stats_by_lang.keys()):
        curr_line = lang
        for dep in sorted_deps:
            curr_line += "\t{0}".format(stats_by_lang[lang][dep])
        print(curr_line)

if __name__ == "__main__":
    main()
