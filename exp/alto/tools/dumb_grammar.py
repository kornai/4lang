from __future__ import print_function
import sys


def main():
    print("interpretation graph: de.up.ling.irtg.algebra.graph.GraphAlgebra")
    print()
    print('S! -> _root(X)\n[graph] merge("(ROOT / ROOT :root (d<dep>))", r_dep(?1))')  # nopep8
    for line in sys.stdin:
        dep = line.strip()
        if dep == 'root':
            continue
        cfg_rule = 'X -> _{0}(X, X)'.format(dep.replace(':', '_'))
        graph_rule = '[graph] r_gov_root(f_dep(merge(merge(r_gov(?1), "(g<gov> :{0} (d<dep>))"), r_dep(?2))))'.format(dep.replace(':', '_'))  # nopep8
        print(cfg_rule)
        print(graph_rule)
        print()


if __name__ == "__main__":
    main()
