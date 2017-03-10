from unidecode import unidecode


REPLACE_MAP = {
    ":": "COLON",
    ",": "COMMA",
    ".": "PERIOD",
    ";": "SEMICOLON",
    "-": "HYPHEN",
    "[": "LSB",
    "]": "RSB",
    "(": "LRB",
    ")": "RRB",
    "{": "LCB",
    "}": "RCB",
    "!": "EXC",
    "?": "QUE",
    "'": "SQ",
    '"': "DQ",
    "/": "PER",
    "\\": "BSL",
    "#": "HASHTAG",
    "%": "PERCENT",
    "&": "ET",
    "@": "AT",
    "$": "DOLLAR",
    "*": "ASTERISK",
    "^": "CAP",
    "`": "IQ",
    "+": "=",
    "|": "PIPE",
    "~": "TILDE",
    "<": "LESS",
    ">": "MORE",
    "=": "EQ"
    }

KEYWORDS = set(["feature"])


def sanitize_word(word):
    word = unidecode(word.decode('utf-8')).encode('utf-8')
    for patt, tgt in REPLACE_MAP.iteritems():
        word = word.replace(patt, tgt)
    for digit in "0123456789":
        word = word.replace(digit, "DIGIT")
    if word in KEYWORDS:
        word = word.upper()
    return word
