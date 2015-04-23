# simple parser for English Wiktionary
from HTMLParser import HTMLParser
import re
import sys

from xml_parser import XMLParser

class WiktParser(XMLParser):

    html_parser = HTMLParser()

    defs_section_regex = re.compile("^#.*?^=", re.M | re.S)
    def_regex = re.compile("^#([^#:\*].*)", re.M)
    double_curly_regex = re.compile("{{.*?}}")
    replacements = [(re.compile(pattern), subst) for pattern, subst in [
        ("\[\[(.*?)\|(.*?)\]\]", "\\2")]]
    patterns_to_remove = [re.compile(pattern) for pattern in [
        "\[\[", "\]\]", "''", "''"]]

    @staticmethod
    def get_pages(text):
        return WiktParser.iter_sections('page', text)

    @staticmethod
    def parse_definition(definition):
        d = definition.strip()
        d = WiktParser.html_parser.unescape(d)
        d = WiktParser.double_curly_regex.sub('', d)
        for pattern, subst in WiktParser.replacements:
            d = pattern.sub(subst, d)
        for pattern in WiktParser.patterns_to_remove:
            d = pattern.sub("", d)

        return d.strip()

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
        if ":" in headword:
            return None
        definitions = WiktParser.get_definitions(page)
        if not definitions:
            return None
        return {"headword": headword, "definitions": definitions}

    @staticmethod
    def parse_xml(xml):
        for page in WiktParser.get_pages(xml):
            parsed_page = WiktParser.parse_page(page)
            if parsed_page is not None:
                yield parsed_page


def test():
    xml = sys.stdin.read()
    for entry in WiktParser.parse_xml(xml):
        print entry

if __name__ == "__main__":
    test()
