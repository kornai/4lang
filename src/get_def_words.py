import sys
from longman_parser import LongmanParser

def main():
    dictionary = LongmanParser.parse_file(sys.argv[1])
    for entry in dictionary['entries']:
        def_words = set()
        for sense in entry['senses']:
            def_words |= sense['definition']
