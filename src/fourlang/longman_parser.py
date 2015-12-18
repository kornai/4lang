#!/usr/bin/env python
# Module for reading Longman XML and producing JSON output

from collections import defaultdict
import json
import re
import sys

from xml_parser import XMLParser

assert json  # silence pyflakes

class LongmanParser(XMLParser):

    @staticmethod
    def add_suffixes(text):
        return re.sub(" <SUFFIX> (.*?) </SUFFIX>", "\\1", text)

    @staticmethod
    def remove_extra_whitespace(text):
        if text is None:
            return None
        return " ".join(text.split()).strip()

    @staticmethod
    def clean_definition(definition):
        if definition is None:
            return definition
        for tag in ("TEXT", "NonDV", "REFHWD", "FULLFORM", "PRON",
                    "PronCodes", "ABBR"):
            definition = LongmanParser.remove_tags(tag, definition)
        for tag in ("REFSENSENUM", "REFHOMNUM", "GLOSS"):
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
    def get_headword(entry_text):
        """Return the first group of "HWD" in entry_text"""
        return LongmanParser.remove_extra_whitespace(
            LongmanParser.get_section("HWD", entry_text))

    @staticmethod
    def get_pos(entry_text):
        return LongmanParser.remove_extra_whitespace(
            LongmanParser.get_section("POS", entry_text))

    @staticmethod
    def parse_entry(entry_text):
        """ """
        entry = {
            "hw": LongmanParser.get_headword(entry_text),
            "senses": map(
                LongmanParser.parse_sense,
                LongmanParser.iter_sections("Sense", entry_text)),
        }

        pos = LongmanParser.get_pos(entry_text)
        for sense in entry['senses']:
            sense['pos'] = pos

        hom_num = LongmanParser.get_section('HOMNUM', entry_text)
        if hom_num is not None:
            entry['hom_num'] = hom_num.strip()

        return entry

    @staticmethod
    def parse_xml(xml_text):
        """Give items of generator of "Entry" strings in xml_text to
        'parse_entry' method one by one."""
        for raw_entry in LongmanParser.iter_sections("Entry", xml_text):
            yield LongmanParser.parse_entry(raw_entry)

    @staticmethod
    def print_defs(longman_obj):
        for entry in longman_obj:
            for sense in entry['senses']:
                print u"{0}\t{1}".format(
                    entry['hw'], sense['definition']).encode("utf-8")

    @staticmethod
    def print_sorted_defs(longman_obj):
        index = defaultdict(list)
        for e in longman_obj:
            index[e['hw']].append(e)
        for hw in sorted(index.iterkeys()):
            for entry in index[hw]:
                for sense in entry['senses']:
                    print u"{0}\t{1}".format(
                        hw, sense['definition']).encode("utf-8")


if __name__ == "__main__":
    LongmanParser.print_sorted_defs(LongmanParser.parse_file(sys.argv[1]))
