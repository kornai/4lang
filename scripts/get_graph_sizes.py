import sys

from pymachine.utils import MachineGraph

from fourlang.lexicon import Lexicon

lexicon = Lexicon.load_from_binary(sys.argv[1])
total = 0
total_size = 0
smallest = 999
largest = 0
for word, machines in lexicon.ext_lexicon.iteritems():
    machine = next(iter(machines))
    graph = MachineGraph.create_from_machines([machine])
    size = len(graph.G) - 1
    if size < 1:
        continue
    total += 1
    total_size += size
    smallest = min(smallest, size)
    largest = max(largest, size)

print 'processed {0} graphs'.format(total)
print 'average size: {0} nodes'.format(total_size/float(total))
print 'smallest: {0}, largest: {1}'.format(smallest, largest)
