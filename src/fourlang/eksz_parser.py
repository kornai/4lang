#!/usr/bin/env python
# Module for reading Longman XML and producing JSON output

import json
import sys

from xml_parser import XMLParser

assert json  # silence pyflakes

class EkszParser(XMLParser):
    @staticmethod
    def parse_headword(sense):
        hw = EkszParser.get_section("LEMMA", sense)
        hom_num = int(EkszParser.get_section("HOM", hw))
        hw = EkszParser.remove_sections("HOM", hw)
        return hw, hom_num

    @staticmethod
    def parse_sense(sense):
        hw, hom_num = EkszParser.parse_headword(sense)
        definition = EkszParser.get_section('DEF', sense)
        pos = EkszParser.get_section('POS', sense)
        return hw, hom_num, pos, definition

    @staticmethod
    def get_entries(xml_text):
        completed_hws = set()
        curr_hw = None
        curr_pos = None
        curr_senses = []
        for sense in EkszParser.iter_sections("SENSE", xml_text):
            hw, hom_num, pos, definition = EkszParser.parse_sense(sense)
            if hom_num > 1:
                continue  # temporary solution
            if curr_hw is None:  # first line
                curr_hw = hw
            elif curr_hw != hw:
                if hw in completed_hws:
                    sys.stderr.write(
                        "INPUT NOT SORTED BY HW: {0}\n".format(hw))
                    sys.exit(-1)
                else:
                    completed_hws.add(hw)

                yield {
                    "hw": curr_hw,
                    "pos": curr_pos if curr_pos is not None else pos,
                    "senses": curr_senses}

                curr_pos = pos  # we'll use the pos of the first occurence
                curr_hw = hw
                curr_senses = []

            curr_senses.append({"definition": definition})

    @staticmethod
    def parse_xml(xml_text):
        """Give items of generator of "Entry" strings in xml_text to
        'parse_entry' method one by one."""
        for entry in EkszParser.get_entries(xml_text):
            yield entry

    @staticmethod
    def print_defs(eksz_obj):
        for entry in eksz_obj:
            for sense in entry['senses']:
                print u"{0}\t{1}".format(
                    entry['hw'], sense['definition']).encode("utf-8")


if __name__ == "__main__":
    # EkszParser.print_defs(EkszParser.parse_file(sys.argv[1]))
    with open(sys.argv[2], 'w') as out_file:
        json.dump(list(EkszParser.parse_file(sys.argv[1])), out_file)
