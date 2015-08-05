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
            if section is not None:
#               print 'start'
                print
                print section['hw'].encode('utf-8')
                if 'redirect' in section:
                    print textwrap.fill(
                        'redirect: ' + section['redirect'],
                        initial_indent='    ',
                        subsequent_indent='        ').encode('utf-8')
#               print "section: " + str(section)
                for sense in section['senses']:
                    print textwrap.fill(
                        sense['definition'],
                        initial_indent='    ',
                        subsequent_indent='        ').encode('utf-8')
#               print
#               print 'end'

    @staticmethod
    def parse_file(input_file):
        for line in iter(open(input_file)):
#            print type(line)
            yield MagyarParser.parse_entry(line.decode('utf-8').strip())

    @staticmethod
    def parse_entry(entry):
#       print 'type of entry: ' + str(type(entry))
        if entry[:6] == '<entry':
            entry_dict = {'hw': MagyarParser.get_hw(entry),
                          'senses': MagyarParser.get_senses(entry)}
        else:
            entry_dict = None
        if entry[:8] == '<entryxr':
            entry_dict['redirect'] = MagyarParser.get_xr(entry)
        return entry_dict

    @staticmethod
    def get_hw(entry):
        hw = re.search('<lemma>(.+)</lemma>', entry, re.S).group(1)
        return re.sub('<hom>[1-9]</hom>', '', hw)

    @staticmethod
    def get_senses(entry):
        raw_sense_list = re.findall(
            '<mainsens>.*?<def>(.*?)</def>.*?</mainsens>', entry)
        modified_sense_list = []
        for sense in raw_sense_list:
            modified_sense_list.append(
                {'definition': MagyarParser.clean_definition(sense)})
        return modified_sense_list

    @staticmethod
    def get_xr(entry):
        redirect = re.search('<xr>(.+)</xr>', entry).group(1)
        return re.sub('<hom>[1-9]</hom>', '', redirect)

    @staticmethod
    def clean_definition(definition):
        tags = ['gloss', 'hint', 'mention', 'syn', ]
        for tag in tags:
            definition = re.sub('</?' + tag + '>', '', definition)
        return definition


if __name__ == "__main__":
    MagyarParser.print_definitions(MagyarParser.parse_file(sys.argv[1]))
