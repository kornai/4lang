import sys
import re
import textwrap


class CollinsParser():
    @staticmethod
    def print_definitions(definitions):
 #       print definitions
        for section in definitions:
 #           print 'start'
            print
            print section['hw']
 #           print "section: " + str(section)
#            print textwrap.fill(section['pos'], initial_indent='    ')
            for sense in section['senses']:
                print textwrap.fill(sense['pos'], initial_indent='    ',
                    subsequent_indent='        ')
                print textwrap.fill(sense['definition'], initial_indent='    ',
                    subsequent_indent='        ')
            print
 #           print 'end'

    @staticmethod
    def parse_file(input_file):
 #       for line in iter(open(input_file)):
 #            print line
 #            yield MagyarParser.parse_entry(line)
        for section in re.split('#[hH]', CollinsParser.get_text(input_file)):
            yield CollinsParser.parse_entry(section)

    @staticmethod
    def pattern_obj(pattern):
 #       print "pattern_obj returns: " + str(type(re.compile(pattern, re.S)))
        return re.compile(pattern, re.S)

    @staticmethod
    def get_text(input_file):
        text = open(input_file).read().decode('utf-8')
        if text[:2] == '#h' or text[:2] == '#H':
            return text[2:]
        else:
            return text

    @staticmethod
    def parse_entry(entry):
 #       return entry
 #       return re.sub(
 #           CollinsParser.multiple_patterns(['#+', '@.', '?!']),
 #           "",
 #           entry)
        if entry == " ":
            return None
        entry = re.sub('@=', '-', entry)
#        entry = re.sub('\n', ' ', entry)
        for pattern in ['\n', '@n']:
            entry = re.sub(pattern, " ", entry)
        for pattern in ['#\+', '@\.', '\?!', '#5\(.*?\)', '#5\[.*?\]',
                        'or #3[^ ]+']:  # '#3' another spelling
            entry = re.sub(pattern, "", entry)
        return {'hw': CollinsParser.get_hw(entry),
            'senses': CollinsParser.get_senses(entry)}

    @staticmethod
    def get_pos(entry):
        # first #6 except #6or
        match = re.search('#6(?!or)(.+?)[. ]', entry, re.S)
        if match:
            return match.group(1)
        else:
            return 'unknown'

    @staticmethod
    def get_hw(entry):
#        print 'entry: ' + entry
        return re.search('(.+?)#[56]', entry, re.S).group(1)

    @staticmethod
    def get_senses(entry):
 #       print 'Entry: ' + entry + '.'
#        description = re.search('#[56](.+)', entry, re.S).group(1)
        description = entry
 #       print 'Description: ' + description + '.'
        if '#1$D' in description:  # check multiple senses for word
#            print 'detected multiple senses in: ' + description
            return CollinsParser.del_pronunciation(
                CollinsParser.get_multiple_senses(description))
        else:
            return CollinsParser.del_pronunciation(
                CollinsParser.get_mono_sense(description))

    @staticmethod
    def del_pronunciation(lst_of_senses):
        for sense in lst_of_senses:
            if sense['definition'][0] == '(':
                re.sub('\(.*?\)', '', sense['definition'], count=1)
#        print 'without pronunciation: ' + repr(lst_of_senses)
        return lst_of_senses

    @staticmethod
    def get_mono_sense(description):
        def_and_pos = CollinsParser.separate_def_and_pos(description)
        definition = def_and_pos[1]
        pos = def_and_pos[0]
        return [{'definition': definition,
                 'pos': pos}]
#        return [{'definition': description,
##                 'pos': CollinsParser.get_pos(description)}]
#                 'pos': CollinsParser.get_pos_from_sense(description)}]

    @staticmethod
    def separate_def_and_pos(description):
#        print 'searching hw in: ' + description
        pos_and_def = re.search('#6(n|abbrev|interj)\.(.*)', description)
        if pos_and_def:
#            print 'hw found: ' + pos_and_def.group(1)
            return (pos_and_def.group(1), pos_and_def.group(2))
        else:
#            print 'hw not found'
            return ('unknown', description)


#    @staticmethod
#    def get_pos_from_sense(sense):
#        pos = re.search('#6(n|abbrev).', sense)
#        if pos:
#            return pos.group(1)
#        else:
#            return 'unknown'

    @staticmethod
    def get_multiple_senses(description):
#        lst = []
#        is_first = True
#        for sense in unicode.split(description, '#1$D'):
#            if is_first:
# #               print 'Sense: ' + sense + '.'
#                if '#5' in sense:
#                    if '#' not in re.findall('#5', sense)[-1]:  # ellenorizni
#                         lst.append(re.findall('#5', sense)[-1])
#                else:
#                    lst.append(sense)
#            else:
#                lst.append({'definition': sense,
##                            'pos': CollinsParser.get_pos(description)})
#                            'pos': CollinsParser.get_pos_from_sense(sense)})
#                # every sense gets pos of first sense!
#            is_first = False
#        return lst

        lst = []
        for sense in unicode.split(description, '#1$D'):  # todo: sense without #5 is not sense
#            print 'next sense: ' + sense
            def_and_pos = CollinsParser.separate_def_and_pos(sense)
            definition = def_and_pos[1]
            pos = def_and_pos[0]
            lst.append({'definition': definition,
                     'pos': pos})
#        print 'list of senses: ' + repr(lst)
        return lst


if __name__ == "__main__":
    CollinsParser.print_definitions(CollinsParser.parse_file(sys.argv[1]))
