import sys

from common.hgraph.hgraph import Hgraph

def main():
    graphs = set([line.strip().split('\t')[0] for line in file(sys.argv[1])])
    for i, graph in enumerate(graphs):
        g = Hgraph.from_string(graph)
        g.render_to_file("{0}_{1}.jpg".format(sys.argv[2], i))

if __name__ == "__main__":
    main()
