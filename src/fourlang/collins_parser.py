import logging
import sys
import re
import textwrap


class CollinsParser():
    @staticmethod
    def print_definitions(definitions):
        """Print CollinsParser's output in human readable form."""
        for section in definitions:
            print
            print section['hw']
            for sense in section['senses']:
                print textwrap.fill(sense['pos'], initial_indent='    ',
                    subsequent_indent='        ')
                print textwrap.fill(sense['definition'], initial_indent='    ',
                    subsequent_indent='        ')
            print

    @staticmethod
    def parse_file(input_file):
        for section in re.split('#[hH]', CollinsParser.get_text(input_file)):
            # sections are separated by #h or #H marks
            yield CollinsParser.parse_entry(section)

    @staticmethod
    def pattern_obj(pattern):
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
        """Delete unnecessary marks
        and return entry in appropriate format."""
        if entry == " ":
            return None
        from_ = ['@=', '\?&', '@!', ' esp.']
        to = ['-', '&', '!', ' especially']
        for f, t in zip(from_, to):
            entry = re.sub(f, t, entry)
        for pattern in ['\n', '@n']:
            entry = re.sub(pattern, " ", entry)
        alternate_forms = CollinsParser.get_alternate_forms(entry)
        for pattern in ['#\+', '@\.', '\?!',
                        'or #3[^ ]+']:  # '#3' another spelling
            entry = re.sub(pattern, "", entry)
        for pattern in ['#5\(.*?\)', '#5\[.*?\]']:
            entry = re.sub(pattern, '#5', entry)
        hw, description = CollinsParser.get_hw(entry)
        return {'hw': hw,
            'senses': CollinsParser.get_senses(description),
            'alternate_forms': alternate_forms}

    @staticmethod
    def get_alternate_forms(entry):
        forms = re.findall('#3(.*?)#[56]', entry)
        return [
            form.replace('#+', '').replace('@.', '').replace('#4', '').strip()
            for form in forms]

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
        """Return headword."""
        match = re.search('(.+?)#[56](.+)', entry, re.S)
        hw = match.group(1).replace('#4', '').strip()
        description = match.group(2)
        return hw, description

    @staticmethod
    def get_senses(entry):
        """Return sense(s)."""
        description = entry
        if '#1$D' in description:  # check multiple senses for word
            return CollinsParser.del_pronunciation(
                CollinsParser.get_multiple_senses(description))
        else:
            return CollinsParser.del_pronunciation(
                CollinsParser.get_mono_sense(description))

    @staticmethod
    def del_pronunciation(lst_of_senses):
        """Return list of senses without pronunciation."""
        for sense in lst_of_senses:
            if sense['definition'][0] == '(':
                re.sub('\(.*?\)', '', sense['definition'], count=1)
        return lst_of_senses

    @staticmethod
    def get_mono_sense(description):
        """Return list with one dictionary for the single sense."""
        def_and_pos = CollinsParser.separate_def_and_pos(description)
        definition = def_and_pos[1]
        if not definition:
            return []
        pos = def_and_pos[0]
        return [{'definition': definition,
                 'pos': pos}]

    pos_and_def_patt = re.compile(
        '(.*)#6(n|adj|vb|tr|adv|intr|abbrev|pl|interj|prep|prefix|determiner|pron|conj|suffix)\.(.*)')  # nopep8

    @staticmethod
    def separate_def_and_pos(description):
        """Return a tuple of pos and definition of a sense"""
        pos_and_def = CollinsParser.pos_and_def_patt.search(description)
        if pos_and_def:
            pos, definition = pos_and_def.group(2), pos_and_def.group(
                1) + pos_and_def.group(3)
        else:
            pos, definition = 'unknown', description

        definition = definition.strip('.,').strip().replace(
            '#5', '').replace('#4', '').strip('.')
        unnecessary = ['^#6[^ ]*', '#1a', '#6']
        for patt in unnecessary:
            definition = re.sub(patt, '', definition).strip()
        definition = re.sub('@m.*', '', definition).strip('.').strip()
        return pos, definition

    @staticmethod
    def get_multiple_senses(description):

        lst = []
        def_part = ''  # This corrects unnecessary splitting
        pos_for_multiple_senses = 'unknown'
        for sense in unicode.split(description, '#1$D'):
            if def_part:
                sense = def_part + sense
            def_and_pos = CollinsParser.separate_def_and_pos(sense)
            definition = def_and_pos[1]
            if not definition:
                def_part = sense
                continue
            else:
                def_part = ''
            pos = def_and_pos[0]
            if pos == 'unknown':
                pos = pos_for_multiple_senses
            else:
                pos_for_multiple_senses = pos
            lst.append({'definition': definition,
                     'pos': pos})
        return lst

if __name__ == "__main__":
    CollinsParser.print_definitions(CollinsParser.parse_file(sys.argv[1]))
