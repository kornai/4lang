# simple parser for English Wiktionary
from HTMLParser import HTMLParser
import re
import sys

from xml_parser import XMLParser

class WiktParser(XMLParser):

    html_parser = HTMLParser()

    header_regex = re.compile("^=+([^=]*?)=+$", re.M)
    lang_section_regex = re.compile('==English==$.*', re.M | re.S)
    defs_section_regex = re.compile("^=+[^=$]*?=+$[^=]*?^#.*?^=", re.M | re.S)
    def_regex = re.compile("^#([^#:\*].*)", re.M)
    double_curly_regex = re.compile("{{.*?}}")
    replacements = [(re.compile(pattern), subst) for pattern, subst in [
        ("\[\[(.*?)\|(.*?)\]\]", "\\2")]]
    patterns_to_remove = [re.compile(pattern) for pattern in [
        "\[\[", "\]\]", "<ref>.*</ref>", "''", "''"]]

    pos_name_map = {  # entries with categories not listed shall be omitted
        'noun': 'n', 'proper noun': 'n', 'verb': 'v', 'adjective': 'adj',
        'adverb': 'adv', 'initialism': 'n', 'pronoun': 'n',
        'abbreviation': 'n', 'numeral': 'num', 'interjection': 'interj',
        'definitions': 'n',  # this means the POS is unknown
        'preposition': 'prp', 'conjunction': 'conj', 'acronym': 'n',
        'cardinal numeral': 'num', 'cardinal number': 'num', 'number': 'num'}

    @staticmethod
    def get_pages(text):
        return WiktParser.iter_sections('page', text)

    @staticmethod
    def get_pos(section):
        header = WiktParser.header_regex.match(section).group(1).lower()
        if header not in WiktParser.pos_name_map:
            return False
        return WiktParser.pos_name_map[header]

    @staticmethod
    def parse_definition(definition):
        d = definition.strip()
        # semi-colons usually separate two definitions on the same line
        d = d.split(';')[0]
        d = WiktParser.html_parser.unescape(d)
        d = WiktParser.double_curly_regex.sub('', d)
        for pattern, subst in WiktParser.replacements:
            d = pattern.sub(subst, d)
        for pattern in WiktParser.patterns_to_remove:
            d = pattern.sub("", d)

        # if a definition is longer than 300 characters, that's probably a bug
        # and it will cause memory errors when parsing
        d = d[:300]

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

        lang_section = WiktParser.lang_section_regex.search(page)
        if lang_section is None:
            return None

        defs_section = WiktParser.defs_section_regex.search(
            lang_section.group())

        if defs_section is None:
            return None

        pos = WiktParser.get_pos(defs_section.group())
        if pos is False:
            return None

        definitions = WiktParser.get_definitions(defs_section.group())

        if not definitions:
            return None

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
