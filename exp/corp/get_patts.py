import sys
from collections import Counter, defaultdict

from tqdm import tqdm

from utils import get_tsv_sens


def main():
    counter = Counter()
    examples = defaultdict(list)
    n = 0
    for sen in tqdm(get_tsv_sens(sys.stdin)):
        n += 1
        patt = []
        for tok in sen:
            patt.append(tok[-1])

        patt = tuple(patt)
        counter[patt] += 1
        if counter[patt] % 100 == 0:
            examples[patt].append(sen)

    sys.stderr.write(f"processed {n} sentences\n")
    for patt, count in counter.most_common():
        if count < 100:
            break
        ex = "\t".join(
            " ".join(tok[0] for tok in sen) for sen in examples[patt])
        print(f"{count}\t{patt}\t{ex}")


if __name__ == "__main__":
    main()
