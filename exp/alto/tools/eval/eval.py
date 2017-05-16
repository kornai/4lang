import os
import sys


def main():
    for dirname in sys.argv[1:]:
        fn = os.path.join(dirname, 'output')
        lang = dirname.split('/')[-1]
        if not os.path.exists(fn):
            continue
        with open(fn) as f:
            count = 0
            err = 0
            done = False
            for line in f:
                if line.startswith('Done'):
                    done = True
                    break
                count += 1
                if line.strip() == 'null':
                    err += 1
            if count == 0:
                continue
            if done:
                print("{0} sens: {1}, parsed: {2}, coverage: {3:.0%}".format(
                    lang, count, count-err, (count-err)/float(count)))
            else:
                print("{0} sens: {1}, parsed: {2}, coverage: {3:.0%}*".format(
                    lang, count, count-err, (count-err)/float(count)))
    print("* = not done")


if __name__ == "__main__":
    main()
