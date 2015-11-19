import sys

from pymachine.utils import MachineGraph

from fourlang.lexicon import Lexicon

def main():
    lex_fn, word = sys.argv[1:3]
    lex = Lexicon.load_from_binary(lex_fn)
    machines = lex.lexicon.get(word, lex.ext_lexicon.get(word))
    if machines is None:
        print '404 :('
    else:
        graph = MachineGraph.create_from_machines(machines)
        sys.stdout.write(graph.to_dot().encode('utf-8'))

if __name__ == "__main__":
    main()
