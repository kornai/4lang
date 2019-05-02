import sys, getopt
import os
from collections import defaultdict
import re
import networkx as nx
from graphviz import Source
from graphviz import Digraph
import networkx as nx


defs_to_parse = {}
def_states = {}
defs = {}

def readfile(filename):
    with open(filename, encoding='utf-8') as f:
        for line in f:
            l = line.strip().split("\t")
            defs[l[4]] = line
            if len(l) >= 8:
                defs_to_parse[l[4]] = (l[0], l[7])
                def_states[l[4]] = None
            else:
                def_states[l[4]] = 'err'

def d_clean(string):
        s = string
        for c in '\\=@-,\'".!:;':
            s = s.replace(c, '_')
        s = s.replace('$', '_dollars')
        s = s.replace('%', '_percent')
        if s == '#':
            s = '_number'
        keywords = ("graph", "node", "strict", "edge")
        if re.match('^[0-9]', s) or s in keywords:
            s = "X" + s
        return s

def to_dot(graph=None):
    lines = [u'digraph finite_state_machine {', '\tdpi=100;']
    # lines.append('\tordering=out;')
    # sorting everything to make the process deterministic
    d_clean("asd")
    node_lines = []
    for node, n_data in graph.nodes(data=True):
        d_node = d_clean(node)
        printname = d_clean('_'.join(d_node.split('_')[:-1]))
        if 'expanded' in n_data and not n_data['expanded']:
            node_line = u'\t{0} [shape = circle, label = "{1}", \
                    style="filled"];'.format(
                            d_node, printname).replace('-', '_')
        else:
            node_line = u'\t{0} [shape = circle, label = "{1}"];'.format(
                    d_node, printname).replace('-', '_')
            node_lines.append(node_line)
    lines += sorted(node_lines)

    edge_lines = []
    for u, v, edata in graph.edges(data=True):
        if 'color' in edata:
            d_node1 = d_clean(u)
            d_node2 = d_clean(v)
            edge_lines.append(
                    u'\t{0} -> {1} [ label = "{2}" ];'.format(
                        d_clean(d_node1), d_clean(d_node2),
                        edata['color']))

    lines += sorted(edge_lines)
    lines.append('}')
    return u'\n'.join(lines)

def parse_direct_node(node):
    if node.startswith("["):
        return "err node startswith ["
    elif "(" in node:
        return "err ( and [ both in node"
    elif "/" in node:
        return "err / and [ in node"
    nodes = node.split("[")
    
    if nodes[0].isupper():
        return "err upper root node"
    
    stripped_nodes = []
    for node in nodes:
        stripped_nodes.append(node.strip("]"))
    return stripped_nodes

def parse_def(definition, def_id):
    nodes = definition[1].split(",")
    G = nx.DiGraph()
    for i, node in enumerate(nodes):
        node = node.strip()
        node = node.strip("<")
        node = node.strip(">")
        node_split = node.split()
        node_split[0] = node_split[0].strip("<")
        node_split[0] = node_split[0].strip(">")
        if len(node_split) > 3:
            def_states[def_id] = 'err'
            return
        if len(node_split) == 3:
            if not node_split[1].isupper():
                def_states[def_id] = 'err not well formatted'
                return
            if node_split[0].isupper() or node_split[2].isupper():
                def_states[def_id] = 'err not well formatted'
                return
            node_split[1] = node_split[1].strip(">")
            node_split[1] = node_split[1].strip("<")
            node_split[2] = node_split[2].strip(">")
            node_split[2] = node_split[2].strip("<")
            
            if "[" in node_split[0]:
                ret_value = parse_direct_node(node_split[0])
                if type(ret_value) == str:
                    def_states[def_id] = ret_value
                    return
                else:
                    for j,node in enumerate(ret_value):
                        if j != len(ret_value)-1:
                            G.add_edge(node + "_" , ret_value[j+1] + "_" , color = 0)
                    node_split[0] = ret_value[0]
            if "/" in node_split[0]:
                splitted = node_split[0].split("/")
                node_split[0] = splitted[0]
                
            if "/" in node_split[2]:
                splitted = node_split[2].split("/")
                node_split[2] = splitted[0]
                
            if "(" in node_split[0]:
                binaries = node_split[0].split("(")
                if binaries[0] == '':
                    def_states[def_id] = 'err no node found'
                    return
                if len(binaries[1].split()) > 1 or len(binaries[0].split()) > 1:
                    def_states[def_id] = 'err multiple nodes between parentheses'
                    return
                if len(binaries) > 2 or binaries[0].isupper() or binaries[1].isupper():
                    def_states[def_id] = 'err not well formatted'
                    return                
                binaries[1] = binaries[1].strip(")")
                node_split[0] = binaries[1]
                G.add_edge(binaries[1] + "_", binaries[0] + "_", color = 0)
                
            if "[" in node_split[2]:
                ret_value = parse_direct_node(node_split[2])
                if type(ret_value) == str:
                    def_states[def_id] = ret_value
                    return
                else:
                    for j,node in enumerate(ret_value):
                        if j != len(ret_value)-1:
                            G.add_edge(node + "_", ret_value[j+1] + "_" , color = 0)
                    node_split[2] = ret_value[0]
                
            if "(" in node_split[2]:
                binaries = node_split[2].split("(")
                if binaries[0] == '':
                    def_states[def_id] = 'err no node found'
                    return
                if len(binaries[1].split()) > 1 or len(binaries[0].split()) > 1:
                    def_states[def_id] = 'err multiple nodes between parentheses'
                    return
                if len(binaries) > 2 or binaries[0].isupper() or binaries[1].isupper():
                    def_states[def_id] = 'err not well formatted'
                    return
                binaries[1] = binaries[1].strip(")")
                node_split[2] = binaries[1]
                G.add_edge(binaries[1] + "_", binaries[0] + "_", color = 0)
                
            G.add_edge(node_split[1] + "_" + str(i), node_split[0] + "_" , color = 1) 
            G.add_edge(node_split[1] + "_" + str(i), node_split[2] + "_" , color = 2)
            G.add_edge(definition[0] + "_", node_split[1] + "_", color = 0)
            
        if len(node_split) == 2:
            node_split[1] = node_split[1].strip(">")
            node_split[1] = node_split[1].strip("<")
            if (node_split[0].isupper() & node_split[1].isupper()) | (node_split[0].isupper() & node_split[1].isupper()):
                if node_split[0] != "'" and node_split[1] != "'":
                    def_states[def_id] = 'err not well formatted'
                    return
            if "[" in node_split[0]:
                ret_value = parse_direct_node(node_split[0])
                if type(ret_value) == str:
                    def_states[def_id] = ret_value
                    return
                else:
                    for j,node in enumerate(ret_value):
                        if j != len(ret_value)-1:
                            G.add_edge(node + "_", ret_value[j+1] + "_" , color = 0)
                    node_split[0] = ret_value[0]
                
            if "/" in node_split[0]:
                splitted = node_split[0].split("/")
                node_split[0] = splitted[0]
                
            if "/" in node_split[1]:
                splitted = node_split[1].split("/")
                node_split[1] = splitted[0]
                
            if "(" in node_split[0]:
                binaries = node_split[0].split("(")
                if binaries[0] == '':
                    def_states[def_id] = 'err not well formatted'
                    return
                if len(binaries[1].split()) > 1 or len(binaries[0].split()) > 1:
                    def_states[def_id] = 'err not well formatted'
                    return
                if len(binaries) > 2 or binaries[0].isupper() or binaries[1].isupper():
                    def_states[def_id] = 'err not well formatted'
                    return
                binaries[1] = binaries[1].strip(")")
                node_split[0] = binaries[1]
                G.add_edge(binaries[1] + "_", binaries[0] + "_", color = 0)
                
            if "[" in node_split[1]:
                ret_value = parse_direct_node(node_split[1])
                if type(ret_value) == str:
                    def_states[def_id] = ret_value
                    return
                else:
                    for j,node in enumerate(ret_value):
                        if j != len(ret_value)-1:
                            G.add_edge(node + "_", ret_value[j+1] + "_" , color = 0)
                    node_split[1] = ret_value[0]
                    
            if "(" in node_split[1]:              
                binaries = node_split[1].split("(")
                if binaries[0] == '':
                    def_states[def_id] = 'err not well formatted'
                    return
                if len(binaries[1].split()) > 1 or len(binaries[0].split()) > 1:
                    def_states[def_id] = 'err not well formatted'
                    return
                if len(binaries) > 2 or binaries[0].isupper() or binaries[1].isupper():
                    def_states[def_id] = 'err not well formatted'
                    return
                binaries[1] = binaries[1].strip(")")
                node_split[1] = binaries[1]
                G.add_edge(binaries[1] + "_", binaries[0] + "_" , color = 0)
                
            if node_split[0].isupper() and node_split[0] != "'":
                if node_split[1] == "'":
                    G.add_edge(node_split[0] + "_" + str(i), definition[0] + "_", color = 1)
                else:
                    G.add_edge(node_split[0] + "_" + str(i), definition[0] + "_", color = 1)
                    G.add_edge(node_split[0] + "_" + str(i), node_split[1] + "_", color = 2)
                    
            if node_split[1].isupper() and node_split[1] != "'":
                if node_split[0] == "'":
                    G.add_edge(node_split[1] + "_" + str(i), definition[0] + "_", color = 2)
                else:
                    G.add_edge(node_split[1] + "_" + str(i), definition[0] + "_", color = 2)
                    G.add_edge(node_split[1] + "_" + str(i), node_split[0] + "_", color = 1)
                
        if len(node_split) == 1:
            if node_split[0].isupper():
                def_states[def_id] = 'err not well formatted'
                return
            
            if "[" in node_split[0]:
                ret_value = parse_direct_node(node_split[0])
                if type(ret_value) == str:
                    def_states[def_id] = ret_value
                    return
                else:
                    for j,node in enumerate(ret_value):
                        if j != len(ret_value)-1:
                            G.add_edge(node + "_", ret_value[j+1] + "_" , color = 0)
                    node_split[0] = ret_value[0]
                
            if "/" in node_split[0]:
                node_split[0] = node_split[0].split("/")[0]     
                
            if "(" in node_split[0]:
                binaries = node_split[0].split("(")
                if len(binaries[1].split()) > 1 or len(binaries[0].split()) > 1:
                    def_states[def_id] = 'err not well formatted'
                    return
                if binaries[0] == '':
                    def_states[def_id] = 'err not well formatted'
                    return
                if len(binaries) > 2 or binaries[0].isupper() or binaries[1].isupper():
                    def_states[def_id] = 'err not well formatted'
                    return
                binaries[1] = binaries[1].strip(")")
                node_split[0] = binaries[1]
                G.add_edge(binaries[1] + "_", binaries[0] + "_", color = 0)
                
            G.add_edge(definition[0] + "_", node_split[0] + "_", color = 0)
    return G

def filter_def(definition, def_id):
    pat = re.search(r".*=.*", definition[1])
    pat_dir = re.search(r"\[(.+)\]", definition[1])
    pat_dir_err = re.search(r"\[([\w]+),[\w]\]", definition[1])
    pat_dir_sp = re.search(r"\[([\w]+)\s([\w]+)\]", definition[1])
    pat_sp = re.search(r"\(([\w]+)\s([\w]+)\)", definition[1])
        
    if not definition[1]:
        def_states[def_id] = 'err no definition'
    elif pat_dir_sp or pat_sp:
        def_states[def_id] = 'err found space between parentheses'
    elif pat_dir_err:
        def_states[def_id] = 'err found enumeration between parentheses'
    elif pat:
        def_states[def_id] = 'err found deep case'
    else:
        print(definition)
        G = parse_def(definition, def_id)
        if G is not None:
            d = to_dot(G)
            return d
        return None

def process(outputdir):
    for element in defs_to_parse:
        d = filter_def(defs_to_parse[element], element)
        if d is not None:
            with open(outputdir  + defs_to_parse[element][0] + "_" + element + ".dot", "w+") as o:
                print(d, file=o)
                
def main(argv):
    inputfile = ''
    outputdir = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","odir="])
    except getopt.GetoptError:
        print('4lang_parser.py -i <inputfile> -o <outputdir>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('4lang_parser.py -i <inputfile> -o <outputdir>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--odir"):
            outputdir = arg
    f = inputfile
    print(inputfile)
    readfile(f)
    o = outputdir
    process(o)
    errors = []
    for state in def_states:
        if def_states[state] and 'err' in def_states[state]:
            errors.append(defs[state].strip() + "\t" + def_states[state] + "\n")
    errors.sort()
    with open(outputdir + "4lang_def_errors", 'w', encoding="utf-8") as f:
        for item in errors:
            f.write("%s" % item)

if __name__ == "__main__":
    main(sys.argv[1:])
