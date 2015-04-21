# simple parser for English Wiktionary
import re
import sys

from xml_parser import XMLParser

class WiktParser(XMLParser):

    def_regex = re.compile("^#([^:\*].*)", re.M)
    double_curly_regex = re.compile("{{.*?}}")

    @staticmethod
    def get_pages(text):
        return WiktParser.iter_sections('page', text)

    @staticmethod
    def parse_definition(definition):
        d = definition.strip()
        d = WiktParser.double_curly_regex.sub('', d)
        return d

    @staticmethod
    def parse_page(page):
        headword = WiktParser.get_section('title', page)
        raw_definitions = WiktParser.def_regex.findall(page)
        parsed_definitions = map(WiktParser.parse_definition, raw_definitions)
        return {"headword": headword, "definitions": parsed_definitions}

    @staticmethod
    def parse_xml(xml):
        for page in WiktParser.get_pages(xml):
            yield WiktParser.parse_page(page)


def test():
    xml = sys.stdin.read()
    for entry in WiktParser.parse_xml(xml):
        print entry

if __name__ == "__main__":
    test()
