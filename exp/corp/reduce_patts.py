import random
import sys
from collections import Counter, defaultdict


def main():
    patts = Counter()
    examples = defaultdict(list)
    for fn in sys.argv[1:]:
        with open(fn) as f:
            for line in f:
                fields = line.strip().split('\t')
                patt = eval(fields[1])
                patts[patt] += int(fields[0])
                examples[patt] += fields[2:]

    for patt, count in patts.most_common():
        sample_size = min(100, len(examples[patt]))
        ex = random.sample(examples[patt], sample_size)
        ex_str = "\t".join(ex)
        print(f"{count}\t{patt}\t{ex_str}")


if __name__ == "__main__":
    main()
