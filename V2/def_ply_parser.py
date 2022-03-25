# Copyright © 2021 Adam Kovacs <adaam.ko@gmail.com>
# Distributed under terms of the MIT license.

from ply import lex
from ply.lex import TOKEN
import ply.yacc as yacc
import sys
import getopt
import argparse
import os
import re


BINARIES = []
with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "binaries"),
    "r",
    encoding="utf-8",
) as f:
    for line in f:
        BINARIES.append(line.strip())
BINARIES.sort(key=lambda x: len(x), reverse=True)


class FourlangLexer:
    def __init__(self):
        self.lexer = lex.lex(module=self)

    tokens = (
        "CLAUSE",
        "RELATION",
        "PUNCT",
        "SQUAREBR",
        "SQUAREBL",
        "ROUNDBR",
        "ROUNDBL",
        "EQUAL",
        "CURLYBR",
        "CURLYBL",
        "ANGLEBR",
        "ANGLEBL",
    )

    t_ignore = " \t"

    # r'(\b(?!FOLLOW|AT|INTO|HAS|ABOUT)\b[a-zA-Z]+)|(^[a-zA-Z]+\/[0-9]+)|(^@[a-zA-Z]+)|(^"[a-zA-Z]+"$)|(^/=[A-Z]+)'
    t_PUNCT = r","
    t_SQUAREBR = r"\]"
    t_SQUAREBL = r"\["
    t_ROUNDBR = r"\)"
    t_ROUNDBL = r"\("
    t_CURLYBR = r"\}"
    t_CURLYBL = r"\{"
    t_ANGLEBR = r"\>"
    t_ANGLEBL = r"\<"

    @TOKEN(fr'(({"|".join(BINARIES)})\/[0-9]+)|({"|".join(BINARIES)})')
    def t_RELATION(self, t):
        return t

    @TOKEN(r"([a-zA-Z-]+[_]*\/[0-9]+)|(@[a-zA-Z-]+[_]*)|([a-zA-Z-]+[_]*)")
    def t_CLAUSE(self, t):
        return t

    @TOKEN(r"(=pat|=agt)")
    def t_EQUAL(self, t):
        return t

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print("Invalid Token:", t.value[0])
        raise TypeError("Invalid token %r" % (t.value[0],))
        t.lexer.skip(1)


class FourlangParser:
    def __init__(self, lexer):
        self.parser = yacc.yacc(module=self, debug=True, write_tables=True)
        self.lexer = lexer

    def parse(self, elements):
        return self.parser.parse(elements)

    tokens = FourlangLexer.tokens
    precedence = (
        ("left", "ANGLEBL"),
        ("left", "ANGLEBR"),
        ("left", "CURLYBL"),
        ("left", "CURLYBR"),
        ("left", "EQUAL"),
        ("left", "ROUNDBL"),
        ("left", "ROUNDBR"),
        ("left", "SQUAREBL"),
        ("left", "SQUAREBR"),
        ("left", "PUNCT"),
        ("left", "CLAUSE"),
        ("left", "RELATION"),
    )

    def p_start(self, p):
        """start : expr rec"""
        print("p_start")

    def p_rec(self, p):
        """rec : PUNCT expr rec
        |"""
        print("p_rec")

    def p_clause(self, p):
        """expr : CLAUSE"""
        print(p[0])
        print(p[1])
        print("p_clause")

    def p_relation(self, p):
        """expr : RELATION"""
        print(p[0])
        print(p[1])
        print("p_relation")

    def p_clause_angle(self, p):
        """expr : ANGLEBL start ANGLEBR"""
        print(p[0])
        print(p[1])
        print("p_clause_angle")

    def p_expr_curly(self, p):
        """expr : CURLYBL start CURLYBR"""
        print(p[0])
        print(p[1])
        print("p_expr_curly")

    def p_equal(self, p):
        "expr : EQUAL"
        print(p[0])
        print(p[1])
        print("p_equal")

    def p_relation_clause(self, p):
        "expr : RELATION start"
        print(p[0])
        print(p[1])
        print("p_relation_clause")

    def p_relation_clause_binary(self, p):
        "expr : start RELATION start"
        print(p[0])
        print(p[1])
        print("p_relation_clause_binary")

    def p_clause_relation(self, p):
        "expr : start RELATION"
        print(p[0])
        print(p[1])
        print("p_clause_relation")

    def p_square(self, p):
        """expr : expr SQUAREBL start SQUAREBR
        | EQUAL SQUAREBL start SQUAREBR
        | RELATION  SQUAREBL start SQUAREBR
        | CLAUSE  SQUAREBL start SQUAREBR"""
        print(p[0])
        print(p[1])
        print("p_square")

    def p_round(self, p):
        """expr : expr ROUNDBL start ROUNDBR
        | EQUAL ROUNDBL start ROUNDBR
        | RELATION ROUNDBL start ROUNDBR
        | CLAUSE ROUNDBL start ROUNDBR"""
        print(p[0])
        print(p[1])
        print("p_round")

    def p_default(self, p):
        """expr : expr ANGLEBL start ANGLEBR
        | EQUAL ANGLEBL start ANGLEBR
        | RELATION ANGLEBL start ANGLEBR
        | CLAUSE ANGLEBL start ANGLEBR"""
        print(p[0])
        print(p[1])
        print("p_default")

    def p_error(self, p):
        raise TypeError("unknown text at %r" % (p,))


defs_to_parse = {}
def_states = {}
defs = {}


def get_tokens(line, mode="4lang"):
    l = line.strip().split("\t")

    if mode == "4lang":
        definition = l[9]
    elif mode == "def":
        definition = l[0]
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
        definition = l[9]
        def_phrases = re.split(
            """,(?=(?:[^\[\]{}<>]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)""",
            definition,
        )
        filtered_definition = []
        for phrase in def_phrases:
            yield phrase.strip()
    else:
        definition = l[1]
        def_phrases = re.split(
            """,(?=(?:[^\[\]{}<>]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)""",
            definition,
        )
        for phrase in def_phrases:
            yield phrase.strip()


def substitute_root(line, mode="4lang"):
    global BINARIES
    l = line.strip().split("\t")
    if mode == "4lang":
        definition = l[9]
    else:
        definition = l[1]
    def_phrases = re.split(
        """,(?=(?:[^\[\]{}<>]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)""", definition
    )
    for i, phrase in enumerate(def_phrases):
        tokens = re.split(
            """\s(?=(?:[^\[\]{}<>"]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)""",
            phrase.strip(),
        )
        new_tokens = None
        if len(tokens) == 1:
            if tokens[0].startswith("<"):
                default_tokens = tokens[0].strip("<>")
                default_tokens_split = re.split(
                    """\s(?=(?:[^\[\]{}<>"]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)""",
                    default_tokens.strip(),
                )
                if len(default_tokens_split) == 2:
                    if default_tokens_split[0] in BINARIES:
                        new_tokens = "<%s %s %s>" % (
                            l[0],
                            default_tokens_split[0],
                            default_tokens_split[1],
                        )
                    elif default_tokens_split[1] in BINARIES:
                        new_tokens = "<%s %s %s>" % (
                            default_tokens_split[0],
                            default_tokens_split[1],
                            l[0],
                        )
                else:
                    new_tokens = "%s is_a %s" % (l[0], tokens[0])
            else:
                new_tokens = "%s is_a %s" % (l[0], tokens[0])
        elif len(tokens) == 2:
            if tokens[0] in BINARIES:
                new_tokens = "%s %s %s" % (l[0], tokens[0], tokens[1])
            elif tokens[1] in BINARIES:
                new_tokens = "%s %s %s" % (tokens[0], tokens[1], l[0])
        else:
            new_tokens = " ".join(tokens)

        if new_tokens:
            def_phrases[i] = new_tokens

    defin = ", ".join(def_phrases)

    if mode == "4lang":
        substituted_line = "\t".join(l[:9]) + "\t" + defin + "\n"
    else:
        substituted_line = l[0] + "\t" + defin + "\n"

    return substituted_line


def filter_line(line, clause, mode="4lang"):
    l = line.strip().split("\t")
    if mode == "4lang":
        definition = l[9]
        def_phrases = re.split(
            """,(?=(?:[^\[\]{}<>]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)""",
            definition,
        )
        found = False
        filtered_definition = []
        for phrase in def_phrases:
            if clause in phrase:
                filtered_definition.append(phrase.strip())
                found = True
        if found:
            filtered_line = "\t".join(l[:9]) + "\t" + ", ".join(filtered_definition)
            return filtered_line.strip("\n") + "\n"
        else:
            return line
    else:
        definition = l[1]
        def_phrases = re.split(
            """,(?=(?:[^\[\]{}<>]|\[[^\]]*\]|{[^}]*}|<[^>]*>|\([^\)]*\))*$)""",
            definition,
        )
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
    with open(filename, encoding="utf-8") as f:
        next(f)
        for i, line in enumerate(f):
            line = re.sub('"[^"]+"', "", line)
            if mode == "4lang":
                l = line.strip().split("\t")
                if l[6] in defs:
                    print(l[6])
                defs[l[6]] = line
                if len(l) >= 10:
                    if "%" in l[9]:
                        l[9] = l[9].split("%")[0].strip()
                    defs_to_parse[l[6]] = (l[0], l[9])
                    def_states[l[6]] = None
                else:
                    def_states[l[6]] = "err bad columns (maybe spaces instead of TABS?)"
            elif mode == "def":
                l = line.strip()
                assert len(l.split("\t")) == 1, "definitions should be one column"
                defs[i] = line
                defs_to_parse[i] = (None, l)
                def_states[i] = None
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


def process(outputdir, parser):
    for element in defs_to_parse:
        d = defs_to_parse[element][1]
        if d is not None:
            try:
                print(f"Parsing: {d}")
                res = parser.parse(d)
            except TypeError as e:
                def_states[element] = "err syntax error " + str(e)


def get_args():
    parser = argparse.ArgumentParser(
        description="def_ply_parser.py -i <inputfile> -o <outputdir> -f <format> -c <clause>"
    )
    parser.add_argument(
        "-i",
        "--input-file",
        type=str,
        required=True,
        help="The input file, should be a tsv",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        required=True,
        help="The output directory, where the processed files will be stored",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="4lang",
        choices=["4lang", "def", "column"],
        help="Choose the process mode. 4lang expects the full column list, def only excpets a single column with the definitions, column expects 2 columns: the words itself and the definitions",
    )
    parser.add_argument(
        "-c",
        "--clause",
        type=str,
        default=None,
        help="The clause you want to filter the definitions with",
    )
    return parser.parse_args()


def main(argv):
    args = get_args()
    inputf = args.input_file
    outputdir = args.output_dir
    mode = args.format
    clause = args.clause
    # bins = args.binaries
    # get_binaries(bins)

    lexer = FourlangLexer()
    parser = FourlangParser(lexer)

    readfile(inputf, mode)
    process(outputdir, parser)
    errors = []
    correct = []
    for state in def_states:
        if def_states[state] and "err" in def_states[state]:
            errors.append(defs[state].strip() + "\t" + def_states[state] + "\n")
        else:
            correct.append(defs[state])
    errors.sort()
    correct.sort()
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    with open(os.path.join(outputdir, "4lang_def_errors"), "w", encoding="utf-8") as f:
        for item in errors:
            if not item.startswith("%"):
                f.write("%s" % item)
    with open(os.path.join(outputdir, "4lang_def_correct"), "w", encoding="utf-8") as f:
        with open(
            os.path.join(outputdir, "4lang_def_correct_filtered"), "w", encoding="utf-8"
        ) as filtered:
            with open(
                os.path.join(outputdir, "4lang_def_correct_substituted"),
                "w",
                encoding="utf-8",
            ) as substituted:
                with open(
                    os.path.join(outputdir, "top_level_clauses"), "w", encoding="utf-8"
                ) as top_level:
                    with open(
                        os.path.join(outputdir, "tokens"), "w", encoding="utf-8"
                    ) as tokens:
                        with open(
                            os.path.join(
                                outputdir, "4lang_def_correct_substituted_top_level"
                            ),
                            "w",
                            encoding="utf-8",
                        ) as substituted_top_level:
                            for item in correct:
                                if not item.startswith("%"):
                                    if mode != "def":
                                        substituted.write(
                                            "%s" % substitute_root(item, mode)
                                        )

                                        for top in get_top_level_clauses(item, mode):
                                            top_level.write("%s\n" % top)
                                        for top in get_top_level_clauses(
                                            substitute_root(item), mode
                                        ):
                                            substituted_top_level.write("%s\n" % top)
                                        if clause:
                                            filtered.write(
                                                "%s" % filter_line(item, clause, mode)
                                            )
                                    tokens.write("%s" % get_tokens(item, mode))
                                    f.write("%s" % item)


if __name__ == "__main__":
    main(sys.argv[1:])
