from ply import lex
import ply.yacc as yacc

tokens = (
    'CLAUSE',
    'RELATION',
    'PUNCT',
    'SQUAREBR',
    'SQUAREBL',
    'ROUNDBR',
    'ROUNDBL',
    'EQUAL',
)

t_ignore = ' \t'

t_RELATION = r'FOLLOW|AT|INTO|HAS|ABOUT'
t_CLAUSE = r'(^[a-zA-Z]+\/[0-9]+)|(^@[a-zA-Z]+)|(\b(?!FOLLOW|AT|INTO|HAS|ABOUT)\b[a-zA-Z]+)'#r'(\b(?!FOLLOW|AT|INTO|HAS|ABOUT)\b[a-zA-Z]+)|(^[a-zA-Z]+\/[0-9]+)|(^@[a-zA-Z]+)|(^"[a-zA-Z]+"$)|(^/=[A-Z]+)'
t_EQUAL = r'(=[A-Z]+)'
t_PUNCT = r','
t_SQUAREBR = r'\]'
t_SQUAREBL = r'\['
t_ROUNDBR = r'\)'
t_ROUNDBL = r'\('


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

def p_equal(p):
    'expr : EQUAL'

def p_relation_clause(p):
    'expr : RELATION expr'

def p_relation_clause_binary(p):
    'expr : expr RELATION expr'

def p_clause_relation(p):
    'expr : expr RELATION'
    print(p[1])

def p_square(p):
    'expr : CLAUSE SQUAREBL expr SQUAREBR'
    print(p[1])
    print(p[3])

def p_round(p):
    'expr : CLAUSE ROUNDBL expr ROUNDBR'

def p_error(p):
    print("Syntax error at '%s'" % p.value)

parser = yacc.yacc()

res = parser.parse("right/1191, =ASD") # the input