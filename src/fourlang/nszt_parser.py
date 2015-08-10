#!usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
# import json
import textwrap


class MagyarParser():
    @staticmethod
    def print_definitions(definitions):
#       with open('magyar_out.json', 'w') as out:
#           json.dump(None, out)
#       for section in definitions:
#           if section != None:
##               print section
#               with open('magyar_out.json', 'a') as out:
#                   json.dump(section, out)
        for section in definitions:
#            if section is not None:
#               print 'start'
            print
#            print "section: " + str(section)
            print section['hw'].encode('utf-8')
            if 'redirect' in section:
                print textwrap.fill(
                    'redirect: ' + section['redirect'],
                    initial_indent='    ',
                    subsequent_indent='        ').encode('utf-8')
            if 'senses' in section:
                for sense in section['senses']:
                    if 'latin' in sense:
                        print textwrap.fill(
                        'latin: ' + sense['latin'],
                        initial_indent='    ',
                        subsequent_indent='        ').encode('utf-8')
                    print textwrap.fill(
                        sense['definition'],
                        initial_indent='    ',
                        subsequent_indent='        ').encode('utf-8')
#               print
#               print 'end'

    @staticmethod
    def parse_file(input_file):
#        for line in iter(open(input_file)):
        for entry in re.finditer('<entry.+?<lemma>.+?</lemma>.*?</entry',
            # avoid entries with empty lemmas
            open(input_file).read().decode('utf-8').strip()):
                yield MagyarParser.parse_entry(entry.group(0))


    @staticmethod
    def parse_entry(entry):
#       print 'type of entry: ' + str(type(entry))
#        if entry[:6] == '<entry':
#            entry_dict = {'hw': MagyarParser.get_hw(entry),
#                          'senses': MagyarParser.get_senses(entry)}
#        else:
#            entry_dict = None
#        if entry[:8] == '<entryxr':
#            entry_dict['redirect'] = MagyarParser.get_xr(entry)
#        return entry_dict

        entry_dict = {'hw': MagyarParser.get_hw(entry)}
        if entry[:8] == '<entryxr':
            entry_dict['redirect'] = MagyarParser.get_xr(entry)
        else:
            entry_dict['senses'] = MagyarParser.get_senses(entry)
# xr?
        return entry_dict

    @staticmethod
    def get_hw(entry):
        hw = re.search('<lemma>(.+?)</lemma>', entry, re.S).group(1)
        tags = ['<hom>[1-9]</hom>', '</?deduced>', '</?reflex>']
        for tag in tags:
            hw = re.sub(tag, '', hw)
        return hw

    @staticmethod
    def get_senses(entry):
        hw = MagyarParser.get_hw(entry)
        if hw[0] == '-' or hw[-1] == '-':  # elotag/utotag
            return [{'definition': MagyarParser.clean_definition(re.search(
                '<def>(.+?)</def>', entry).group(1))}]

        raw_sense_list = re.findall(
            '<mainsens>.*?<def>(.*?)</def>.*?</mainsens>', entry)
        modified_sense_list = []
        for sense in raw_sense_list:
            if sense != '<same/>':
                modified_sense_list.append(
                    {'definition': MagyarParser.clean_definition(sense)})
                if '<tr>' in sense:
                    modified_sense_list[-1]['latin'] = MagyarParser.get_latin(
                        sense)
        return modified_sense_list

    @staticmethod
    def get_xr(entry):
        redirect = re.search('<xr>(.+?)</xr>', entry).group(1)
        return re.sub('<hom>[1-9]</hom>', '', redirect)

    @staticmethod
    def get_latin(sense):
        latin = re.search('<tr>(.+?)</tr>', sense).group(1)
        latin = re.sub('</?sub>', '', latin)
        return latin

    @staticmethod
    def clean_definition(definition):
        tags = ['gloss', 'mention', 'syn', 'tr>.+?</tr', 'hom>[1-9]</hom',
            'sub', 'syn special="no"', 'mean']
        for tag in tags:
            definition = re.sub('</?' + tag + '>', ' ', definition)

        definition = ' ' + definition
        before = ['</?hint>', '<syn special="semicolon">',
            '<syn special="comma">', '<syn special="ill">',
            '<syn special="v">', ' es\.', ' gyakr\.', ' haszn\.', ' ill\.',
            ' kapcs\.', u' kül\.', ' rendsz\.', ' ritk\.', ' v\.',
            ' vonatk\.', u' ált\.', ' vm', ' vki', ' mn ', ' fn ', ' pl.',
            u' ún.',  ' {2,}', ' ,']
        after = ['', '; ', ', ', ' illetve ', ' vagy ', ' esetleg', ' gyakran',
            u' használt', ' illetve', ' kapcsolatos', u' különösen',
            ' rendszerint', u' ritkábban', ' vagy', u' vonatkozó',
            u' általában', ' valam', ' valaki', u' melléknév ', u' főnév ',
            u' például', u' úgynevezett', ' ', ',']
        # places of last two items are important
        for b, a in zip(before, after):
            definition = re.sub(b, a, definition)

#        definition = re.sub('</?hint>', '', definition)
#        definition = re.sub('<syn special="semicolon">', '; ', definition)
#        definition = re.sub('<syn special="comma">', ', ', definition)
#        definition = re.sub('<syn special="ill">', ' illetve ', definition)
#        definition = re.sub(' {2,}', ' ', definition)
#        definition = re.sub(' ,', ',', definition)
        return definition.strip()

    @staticmethod
    def sub(string, pattern, repl):
        pass


if __name__ == "__main__":
    for input_file in sys.argv[1:]:
        MagyarParser.print_definitions(MagyarParser.parse_file(input_file))
