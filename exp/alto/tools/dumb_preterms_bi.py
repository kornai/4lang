from __future__ import print_function
import sys


def main():
    for line in sys.stdin:
        pos = line.strip()
        if pos == '_':
            continue
        cfg_rule = 'X -> _{0}({1})'.format(pos, pos)
        graph_rule = '[graph] ?1'
        fourlang_rule = '[4lang] ?1'
        print(cfg_rule)
        print(graph_rule)
        print(fourlang_rule)
        print()


if __name__ == "__main__":
    main()
