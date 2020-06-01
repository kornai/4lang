import os
import sys


def main():
    total_count = 0
    total_err = 0
    results = []
    dirs = os.listdir(sys.argv[1])
    log_dir = sys.argv[2]
    for dirname in dirs:
        fn = os.path.join(sys.argv[1], dirname, 'output')
        lang = dirname.split('/')[-1]
        if not os.path.exists(fn):
            continue
        with open(fn) as f:
            count = 0
            err = 0
            for line in f:
                count += 1
                total_count += 1
                if line.strip() == 'null':
                    err += 1
                    total_err += 1
            if count == 0:
                continue
            coverage = (count-err) / float(count)
            log_fn = os.path.join(log_dir, lang, 'log')
            with open(log_fn) as lf:
                lines = lf.readlines()
                done = lines and lines[-1].startswith('Done')
            results.append((coverage, count, err, lang, done))

    results.sort(reverse=True)
    print("lang\tsens\tparsed\tcoverage")
    for coverage, count, err, lang, done in results:
        if done:
            print("{0}\t{1}\t{2}\t{3:.0%}".format(
                lang, count, count-err, coverage))
        else:
            print("{0}\t{1}\t{2}\t{3:.0%}*".format(
                lang, count, count-err, coverage))

    print("* = not done")

    print("total sens: {0}, parsed: {1}, coverage: {2:.0%}".format(
        total_count, total_count-total_err,
        (total_count-total_err) / float(total_count)))


if __name__ == "__main__":
    main()
