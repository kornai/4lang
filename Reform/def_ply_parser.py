from ply import lex
import ply.yacc as yacc
import sys, getopt
import os
import re

tokens = (
    'CLAUSE',
    'RELATION',
    'PUNCT',
    'SQUAREBR',
    'SQUAREBL',
    'ROUNDBR',
    'ROUNDBL',
    'EQUAL',
    "CITE",
    "UNDER",
    'CURLYBR',
    'CURLYBL',
    'ANGLEBR',
    'ANGLEBL',
    'DASH'
)

t_ignore = ' \t'

t_RELATION = r'([A-Z]+\/[0-9]+)|([A-Z]+_[A-Z]+)|([A-Z]+)'
t_CLAUSE = r'([a-z-_]+\/[0-9]+)|(@[a-zA-Z-_]+)|(\b(?!FOLLOW|AT|TO|INTO|HAS|ABOUT|ON|IN|IS|PART\_OF|IS\_A|NEXT\_TO|INSTRUMENT|CAUSE|MARK|LACK|ER|FROM|BETWEEN|_)\b[a-zA-Z0-9-_]+)'#r'(\b(?!FOLLOW|AT|INTO|HAS|ABOUT)\b[a-zA-Z]+)|(^[a-zA-Z]+\/[0-9]+)|(^@[a-zA-Z]+)|(^"[a-zA-Z]+"$)|(^/=[A-Z]+)'
t_EQUAL = r'(=[a-zA-Z-_]+)'
t_PUNCT = r','
t_SQUAREBR = r'\]'
t_SQUAREBL = r'\['
t_ROUNDBR = r'\)'
t_ROUNDBL = r'\('
t_CURLYBR = r'\}'
t_CURLYBL = r'\{'
t_ANGLEBR = r'\>'
t_ANGLEBL = r'\<'
t_CITE = '"'
t_UNDER = "_"
t_DASH = "-"

def t_newline( t ):
  r'\n+'
  t.lexer.lineno += len( t.value )

def t_error( t ):
  print("Invalid Token:",t.value[0])
  raise TypeError("Invalid token %r" % (t.value[0],))
  t.lexer.skip( 1 )

lexer = lex.lex()


def p_start(p):
    '''start : expr rec'''

def p_rec(p):
    '''rec : PUNCT expr rec
    |'''

def p_clause(p):
    '''expr : CLAUSE '''
    p[0] = p[1]

def p_clause_angle(p):
    '''expr : ANGLEBL start ANGLEBR'''

def p_cite(p):
  '''expr : CITE CLAUSE CITE'''

def p_dash_cite(p):
  '''expr : CITE UNDER DASH CLAUSE CITE'''

def p_under_cite(p):
  '''expr : CITE UNDER CLAUSE CITE'''

def p_under_slash(p):
  '''expr : CITE CLAUSE UNDER CITE'''

def p_under_slash_relation(p):
  '''expr : CITE RELATION UNDER CITE'''

def p_under_cite_relation(p):
  '''expr : CITE UNDER RELATION CITE'''

def p_under_cite_relation_under(p):
  '''expr : CITE UNDER RELATION UNDER CITE'''

def p_cite_relation(p):
  '''expr : CITE RELATION CITE'''

def p_under_cite_clause_under(p):
  '''expr : CITE UNDER CLAUSE UNDER CITE'''

def p_clause_under_cite_clause_under(p):
  '''expr : CITE CLAUSE UNDER CLAUSE CITE'''

def p_expr_curly(p):
    '''expr : CURLYBL start CURLYBR'''

def p_equal(p):
    'expr : EQUAL'

def p_relation_clause(p):
    'expr : RELATION expr'

def p_equal_clause(p):
    'expr : EQUAL start'

def p_equal_clause_equal(p):
    'expr : EQUAL start EQUAL'

def p_relation_clause_binary(p):
    'expr : expr RELATION expr'

def p_clause_relation(p):
    'expr : expr RELATION'
    #print(p[1])

def p_clause_binary(p):
    'expr : expr CLAUSE expr'

def p_expr_clause(p):
    'expr : expr CLAUSE'
    #print(p[1])

def p_clause_expr(p):
    'expr : CLAUSE expr'

def p_relation(p):
    'expr : RELATION'
    #print(p[1])

def p_square(p):
    '''expr : expr SQUAREBL start SQUAREBR
    | EQUAL SQUAREBL start SQUAREBR
    | RELATION  SQUAREBL start SQUAREBR'''
    #print(p[1])
    #print(p[3])

def p_round(p):
    '''expr : expr ROUNDBL start ROUNDBR
    | EQUAL ROUNDBL start ROUNDBR
    | CITE CLAUSE CITE ROUNDBL start ROUNDBR
    | RELATION ROUNDBL start ROUNDBR'''

def p_error(p):
    raise TypeError("unknown text at %r" % (p,))

parser = yacc.yacc()

defs_to_parse = {}
def_states = {}
defs = {}

def get_tokens(line, mode="4lang"):
    l = line.strip().split("\t")

    if mode == "4lang":
        definition = l[7]
    else:
        definition = l[1]

    tokens = []
    definition = re.sub("@", "", definition)
    definition = re.sub('"', "", definition)
    definition = re.sub(",", " ", definition)
    definition = re.sub("\{", " ", definition)
    definition = re.sub("\}", " ", definition)
    definition = re.sub("\(", " ", definition)
    definition = re.sub("\)", " ", definition)
    definition = re.sub("\[", " ", definition)
    definition = re.sub("\]", " ", definition)
    definition = re.sub("[0-9]*", "", definition)
    definition = re.sub("/", "", definition)
    words = definition.split()
    for wo in words:
        wo = wo.strip()
        if not ">" in wo and not "<" in wo:
            tokens.append(wo)
    
    defin = " ".join(tokens)

    substituted_line = l[0] + "\t" + defin + "\n"

    return substituted_line


def get_top_level_clauses(line, mode="4lang"):
    l = line.strip().split("\t")
    if mode == "4lang":
        definition = l[7]
        def_phrases = re.split(''',(?=(?:[^\[\]{}<>]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)''', definition)
        filtered_definition = []
        for phrase in def_phrases:
            yield phrase.strip()
    else:
        definition = l[1]
        def_phrases = re.split(''',(?=(?:[^\[\]{}<>]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)''', definition)
        for phrase in def_phrases:
            yield phrase.strip()


def substitute_root(line, mode="4lang"):
    l = line.strip().split("\t")
    binary_atom = set()
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "binaries"), 'r', encoding="utf-8") as f:
        for line in f:
            binary_atom.add(line.strip())

    if mode == "4lang":
        definition = l[7]
    else:
        definition = l[1]
    def_phrases = re.split(''',(?=(?:[^\[\]{}<>]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)''', definition)
    for i, phrase in enumerate(def_phrases):
        tokens = re.split('''\s(?=(?:[^\[\]{}<>"]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)''', phrase.strip())
        new_tokens = None
        if len(tokens) == 1:
            if tokens[0].startswith("<"):
                default_tokens = tokens[0].strip("<>")
                default_tokens_split = re.split('''\s(?=(?:[^\[\]{}<>"]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)''', default_tokens.strip())
                if len(default_tokens_split) == 2:
                    if default_tokens_split[0] in binary_atom:
                        new_tokens = "<%s %s %s>" % (l[0], default_tokens_split[0], default_tokens_split[1])
                    elif default_tokens_split[1] in binary_atom:
                        new_tokens = "<%s %s %s>" % (default_tokens_split[0], default_tokens_split[1], l[0])
                else:
                    new_tokens = "%s ISA %s" % (l[0], tokens[0])
            else:
                new_tokens = "%s ISA %s" % (l[0], tokens[0])
        elif len(tokens) == 2:
            if tokens[0] in binary_atom:
                new_tokens = "%s %s %s" % (l[0], tokens[0], tokens[1])
            elif tokens[1] in binary_atom:
                new_tokens = "%s %s %s" % (tokens[0], tokens[1], l[0])
        else:
            new_tokens = " ".join(tokens)

        if new_tokens:
            def_phrases[i] = new_tokens
    
    defin = ", ".join(def_phrases)

    if mode == "4lang":
        substituted_line = "\t".join(l[:7]) + "\t" + defin + "\n"
    else:
        substituted_line = l[0] + "\t" + defin + "\n"

    return substituted_line
        
            
def filter_line(line, clause, mode="4lang"):
    l = line.strip().split("\t")
    if mode == "4lang":
        definition = l[7]
        def_phrases = re.split(''',(?=(?:[^\[\]{}<>]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)''', definition)
        found = False
        filtered_definition = []
        for phrase in def_phrases:
            if clause in phrase:
                filtered_definition.append(phrase.strip())
                found = True
        if found:
            filtered_line = "\t".join(l[:7]) + "\t" + ", ".join(filtered_definition)
            return filtered_line.strip("\n") + "\n"
        else:
            return line
    else:
        definition = l[1]
        def_phrases = re.split(''',(?=(?:[^\[\]{}<>]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)''', definition)
        found = False
        filtered_definition = []
        for phrase in def_phrases:
            if clause in phrase:
                filtered_definition.append(phrase.strip())
                found = True
        if found:
            filtered_line = l[0] + "\t" + ", ".join(filtered_definition)
            return filtered_line.strip("\n") + "\n"
        else:
            return line

def readfile(filename, mode="4lang"):
    with open(filename, encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = re.sub('"[^"]+"', "", line)
            if mode == "4lang":
                l = line.strip().split("\t")
                if l[4] in defs:
                    print(l[4])
                defs[l[4]] = line
                if len(l) >= 8:
                    if "%" in l[7]:
                        l[7] = l[7].split("%")[0].strip()
                    defs_to_parse[l[4]] = (l[0], l[7])
                    def_states[l[4]] = None
                else:
                    def_states[l[4]] = 'err bad columns (maybe spaces instead of TABS?)'
            else:
                l = line.strip().split("\t")
                defs[i] = line
                if len(l) >= 2:
                    if "%" in l[1]:
                        l[1] = l[1].split("%")[0].strip()
                    defs_to_parse[i] = (l[0], l[1])
                    def_states[i] = None
                else:
                    def_states[i] = "err bad columns (maybe spaces instead of TABS?)"

def process(outputdir):
    for element in defs_to_parse:
        d = defs_to_parse[element][1]
        if d is not None:
            try:
                res = parser.parse(d)
            except TypeError as e:
                def_states[element] = "err syntax error " + str(e)

def main(argv):
    inputfile = ''
    outputdir = ''
    mode = "4lang"
    clause = None
    try:
        opts, args = getopt.getopt(argv,"hi:o:f:c:",["ifile=","odir=", "format=", "clause="])
    except getopt.GetoptError:
        print('def_ply_parser.py -i <inputfile> -o <outputdir> -f <format> -c <clause>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('4lang_parser.py -i <inputfile> -o <outputdir> -f <4lang|cut> -c <clause to filter by>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--odir"):
            outputdir = arg
        elif opt in ("-f", "--format"):
            mode = arg
        elif opt in ("-c", "--clause"):
            clause = arg

    f = inputfile
    readfile(f, mode)
    o = outputdir
    process(o)
    errors = []
    correct = []
    for state in def_states:
        if def_states[state] and 'err' in def_states[state]:
            errors.append(defs[state].strip() + "\t" + def_states[state] + "\n")
        else:
            correct.append(defs[state])
    errors.sort()
    correct.sort()
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    with open(os.path.join(outputdir, "4lang_def_errors"), 'w', encoding="utf-8") as f:
        for item in errors:
            if not item.startswith("%"):
                f.write("%s" % item)
    with open(os.path.join(outputdir, "4lang_def_correct"), 'w', encoding="utf-8") as f:
        with open(os.path.join(outputdir, "4lang_def_correct_filtered"), "w", encoding="utf-8") as filtered:
            with open(os.path.join(outputdir, "4lang_def_correct_substituted"), "w", encoding="utf-8") as substituted:
                with open(os.path.join(outputdir, "top_level_clauses"), "w", encoding="utf-8") as top_level: 
                    with open(os.path.join(outputdir, "tokens"), "w", encoding="utf-8") as tokens: 
                        for item in correct:
                            if not item.startswith("%"):
                                substituted.write("%s" % substitute_root(item, mode))
                                for top in get_top_level_clauses(item, mode):
                                    top_level.write("%s\n" % top)
                                if clause:
                                    filtered.write("%s" % filter_line(item, clause, mode))
                                tokens.write("%s" % get_tokens(item, mode))
                                f.write("%s" % item)

if __name__ == "__main__":
    main(sys.argv[1:])
