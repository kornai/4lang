#!/usr/bin/env python
# Module for reading Longman XML and producing JSON output

import json
import re
import sys

assert json  # silence pyflakes

class LongmanParser():

    @staticmethod
    def section_pattern(tag):
        pattern_string = "<{0}>(.*?)</{0}>".format(tag)
        return re.compile(pattern_string, re.S)

    @staticmethod
    def tag_pattern(tag):
        pattern_string = "</?{0}>".format(tag)
        return re.compile(pattern_string, re.S)

    @staticmethod
    def iter_sections(tag, text):
        return LongmanParser.section_pattern(tag).findall(text)

    @staticmethod
    def get_section(tag, text):
        match_obj = LongmanParser.section_pattern(tag).search(text)
        return None if match_obj is None else match_obj.group(1)

    @staticmethod
    def remove_sections(tag, text):
        return LongmanParser.section_pattern(tag).sub("", text)

    @staticmethod
    def remove_tags(tag, text):
        return LongmanParser.tag_pattern(tag).sub("", text)

    @staticmethod
    def add_suffixes(text):
        return re.sub(" <SUFFIX> (.*?) </SUFFIX>", "\\1", text)

    @staticmethod
    def remove_extra_whitespace(text):
        return " ".join(text.split())

    @staticmethod
    def clean_definition(definition):
        if definition is None:
            return definition
        for tag in ("TEXT", "NonDV", "REFHWD", "FULLFORM"):
            definition = LongmanParser.remove_tags(tag, definition)
        for tag in ("REFSENSENUM",):
            definition = LongmanParser.remove_sections(tag, definition)
        definition = LongmanParser.remove_extra_whitespace(definition)
        definition = LongmanParser.add_suffixes(definition)
        return definition

    @staticmethod
    def parse_sense(text):
        definition = LongmanParser.clean_definition(
            LongmanParser.get_section("DEF", text))
        full_form = LongmanParser.get_section("FULLFORM", text)
        return {"full_form": full_form, "definition": definition}

    @staticmethod
    def parse_entry(entry_text):
        return {
            "hw": LongmanParser.remove_extra_whitespace(
                LongmanParser.get_section("HWD", entry_text)),
            "pos": LongmanParser.get_section("POS", entry_text),
            "senses": map(
                LongmanParser.parse_sense,
                LongmanParser.iter_sections("Sense", entry_text)),
        }

    @staticmethod
    def parse_xml(xml_text):
        return {"entries": map(
            LongmanParser.parse_entry,
            LongmanParser.iter_sections("Entry", xml_text))}

    @staticmethod
    def parse_file(fn):
        return LongmanParser.parse_xml(open(fn).read().decode('utf-8'))

    @staticmethod
    def print_defs(longman_obj):
        for entry in longman_obj['entries']:
            for sense in entry['senses']:
                print "{0}\t{1}".format(entry['hw'], sense['definition'])


if __name__ == "__main__":
    #LongmanParser.print_defs(LongmanParser.parse_file(sys.argv[1]))
    json.dump(LongmanParser.parse_file(sys.argv[1]), sys.stdout)
