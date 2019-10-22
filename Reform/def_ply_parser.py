from ply import lex
import ply.yacc as yacc
import sys, getopt
import os

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
    'CURLYBR',
    'CURLYBL',
    'ANGLEBR',
    'ANGLEBL',
)

t_ignore = ' \t'

t_RELATION = r'([A-Z]+\/[0-9]+)|([A-Z]+_[A-Z]+)|([A-Z]+)'
t_CLAUSE = r'([a-z]+\/[0-9]+)|(@[a-zA-Z]+)|(\b(?!FOLLOW|AT|INTO|HAS|ABOUT|ON|IN|IS|PART\_OF|IS\_A|INSTRUMENT|CAUSE|MARK)\b[a-zA-Z]+)'#r'(\b(?!FOLLOW|AT|INTO|HAS|ABOUT)\b[a-zA-Z]+)|(^[a-zA-Z]+\/[0-9]+)|(^@[a-zA-Z]+)|(^"[a-zA-Z]+"$)|(^/=[A-Z]+)'
t_EQUAL = r'(=[A-Z]+)'
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

def t_newline( t ):
  r'\n+'
  t.lexer.lineno += len( t.value )

def t_error( t ):
  print("Invalid Token:",t.value[0])
  t.lexer.skip( 1 )

lexer = lex.lex()


def p_start(p):
    '''start : expr rec'''
    print(p[1])

def p_rec(p):
    '''rec : PUNCT expr rec
    |'''

def p_clause(p):
    '''expr : CLAUSE '''
    p[0] = p[1]

def p_clause_angle(p):
    '''expr : ANGLEBL expr ANGLEBR'''

def p_cite(p):
  '''expr : CITE CLAUSE CITE'''

def p_expr_curly(p):
    '''expr : CURLYBL start CURLYBR'''

def p_equal(p):
    'expr : EQUAL'

def p_relation_clause(p):
    'expr : RELATION expr'

def p_relation_clause_binary(p):
    'expr : expr RELATION expr'

def p_clause_relation(p):
    'expr : expr RELATION'
    #print(p[1])

def p_square(p):
    '''expr : CLAUSE SQUAREBL start SQUAREBR
    | EQUAL SQUAREBL start SQUAREBR'''
    #print(p[1])
    #print(p[3])

def p_round(p):
    '''expr : CLAUSE ROUNDBL expr ROUNDBR
    | EQUAL ROUNDBL expr ROUNDBR
    | CITE CLAUSE CITE ROUNDBL expr ROUNDBR'''

def p_error(p):
    raise TypeError("unknown text at %r" % (p,))

parser = yacc.yacc()

defs_to_parse = {}
def_states = {}
defs = {}

def readfile(filename):
    with open(filename, encoding='utf-8') as f:
        for line in f:
            l = line.strip().split("\t")
            defs[l[4]] = line
            if len(l) >= 8:
                if "%" in l[7]:
                    l[7] = l[7].split("%")[0].strip()
                defs_to_parse[l[4]] = (l[0], l[7])
                def_states[l[4]] = None
            else:
                def_states[l[4]] = 'err bad columns (maybe spaces instead of TABS?)'

def process(outputdir):
    for element in defs_to_parse:
        d = defs_to_parse[element][1]
        if d is not None:
            try:
                res = parser.parse(d)
            except TypeError as e:
                def_states[element] = "err syntax error"

def main(argv):
    inputfile = ''
    outputdir = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","odir="])
    except getopt.GetoptError:
        print('def_ply_parser.py -i <inputfile> -o <outputdir>')
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
            f.write("%s" % item)
    with open(os.path.join(outputdir, "4lang_def_correct"), 'w', encoding="utf-8") as f:
        for item in correct:
            f.write("%s" % item)

if __name__ == "__main__":
    main(sys.argv[1:])