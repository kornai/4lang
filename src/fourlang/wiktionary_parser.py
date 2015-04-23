# simple parser for English Wiktionary
from HTMLParser import HTMLParser
import logging
import re
import sys

from xml_parser import XMLParser

class WiktParser(XMLParser):

    html_parser = HTMLParser()

    header_regex = re.compile("^=+([^=]*?)=+$", re.M)
    defs_section_regex = re.compile("^=+[^=$]*?=+$[^=]*?^#.*?^=", re.M | re.S)
    def_regex = re.compile("^#([^#:\*].*)", re.M)
    double_curly_regex = re.compile("{{.*?}}")
    replacements = [(re.compile(pattern), subst) for pattern, subst in [
        ("\[\[(.*?)\|(.*?)\]\]", "\\2")]]
    patterns_to_remove = [re.compile(pattern) for pattern in [
        "\[\[", "\]\]", "''", "''"]]

    pos_name_map = {
        'noun': 'n', 'adjective': 'adj', 'adverb': 'adv', 'symbol': 'sym'}

    @staticmethod
    def get_pages(text):
        return WiktParser.iter_sections('page', text)

    @staticmethod
    def get_pos(section):
        header = WiktParser.header_regex.match(section).group(1).lower()
        if header not in WiktParser.pos_name_map:
            logging.warning("unknown POS: {0}, returning 'n'".format(header))
            return 'n'
        return WiktParser.pos_name_map[header]

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
    def get_definitions(section):
        raw_definitions = WiktParser.def_regex.findall(section)
        parsed_definitions = map(WiktParser.parse_definition, raw_definitions)
        kept_definitions = filter(None, parsed_definitions)
        return kept_definitions

    @staticmethod
    def parse_page(page):
        headword = WiktParser.get_section('title', page)
        if ":" in headword:
            return None

        defs_section = WiktParser.defs_section_regex.search(page)
        if defs_section is None:
            logging.warning(u'no defs section: {0}'.format(headword))
            definitions = []
        else:
            definitions = WiktParser.get_definitions(defs_section.group())

        if not definitions:
            return None

        pos = WiktParser.get_pos(defs_section.group())

        return {
            "hw": headword,
            "senses": [{
                "full_form": headword,
                "pos": pos,
                "definition": definition}
                for definition in definitions]}

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
