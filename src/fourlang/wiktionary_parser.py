# simple parser for English Wiktionary
import re
import sys

from xml_parser import XMLParser

class WiktParser(XMLParser):

    defs_section_regex = re.compile("^#.*?^=", re.M | re.S)
    def_regex = re.compile("^#([^:\*].*)", re.M)
    double_curly_regex = re.compile("{{.*?}}")

    @staticmethod
    def get_pages(text):
        return WiktParser.iter_sections('page', text)

    @staticmethod
    def parse_definition(definition):
        d = definition.strip()
        d = WiktParser.double_curly_regex.sub('', d)
        d = d.replace("[[", "")
        d = d.replace("]]", "")
        return d

    @staticmethod
    def get_definitions(page):
        defs_section = WiktParser.defs_section_regex.search(page)
        if defs_section is None:
            return []
        raw_definitions = WiktParser.def_regex.findall(defs_section.group())
        parsed_definitions = map(WiktParser.parse_definition, raw_definitions)
        kept_definitions = filter(None, parsed_definitions)
        return kept_definitions

    @staticmethod
    def parse_page(page):
        headword = WiktParser.get_section('title', page)
        definitions = WiktParser.get_definitions(page)
        return {"headword": headword, "definitions": definitions}

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
