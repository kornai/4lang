import logging
import sys
import re


class CollinsParser():
    @staticmethod
    def print_definitions(definitions):
        for section in definitions:
            print section['hw']
            for sense in section['senses']:
                print "{0}\t{1}".format(
                    section['hw'], sense['definition'])

    @staticmethod
    def parse_file(input_file):
        for section in re.split('#[hH]', CollinsParser.get_text(input_file)):
            try:
                yield CollinsParser.parse_entry(section)
            except:
                logging.warning("parse failed on section: {0}".format(section))

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
        if not entry.strip():
            return None
        entry = re.sub('@=', '-', entry)
#        entry = re.sub('\n', ' ', entry)
        for pattern in ['\n', '@n']:
            entry = re.sub(pattern, " ", entry)
        alternate_forms = CollinsParser.get_alternate_forms(entry)
        for pattern in ['#\+', '@\.', '\?!', '#5\(.*?\)', '#5\[.*?\]',
                        'or #3[^ ]+']:  # '#3' another spelling
            entry = re.sub(pattern, "", entry)

        try:
            hw = CollinsParser.get_hw(entry)
        except:
            logging.warning("get_hw failed in entry: {0}".format(entry))
            hw = "???"
        return {
            'hw': hw,
            'senses': CollinsParser.get_senses(entry),
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
        print 'entry: ' + entry
        return re.search('(.+?)#[56]', entry, re.S).group(1).replace(
            '#4', '').strip()

    @staticmethod
    def get_senses(entry):
        """Return sense(s)."""
        if '#1$D' in entry:
            return CollinsParser.del_pronunciation(
                CollinsParser.get_multiple_senses(entry))
        else:
            return CollinsParser.del_pronunciation(
                CollinsParser.get_mono_sense(entry))

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
        if not definition:
            return []
        pos = def_and_pos[0]
        return [{'definition': definition,
                 'pos': pos}]
        # return [{'definition': description,
        #           'pos': CollinsParser.get_pos(description)}]
        #          'pos': CollinsParser.get_pos_from_sense(description)}]

    pos_and_def_patt = re.compile(
        '#6(n|adj|vb|tr|adv|intr|abbrev|pl|interj|prep|prefix|determiner|pron|conj|suffix)\.(.*)')  # nopep8

    @staticmethod
    def separate_def_and_pos(description):
        # print 'searching hw in: ' + description
        pos_and_def = CollinsParser.pos_and_def_patt.search(description)
        if pos_and_def:
            # print 'hw found: ' + pos_and_def.group(1)
            pos, definition = pos_and_def.group(1), pos_and_def.group(2)
        else:
            # print 'hw not found'
            pos, definition = 'unknown', description

        definition = definition.strip('.,').strip().replace(
            '#5', '').replace('#4', '').strip('.')
        definition = re.sub('^#6[^ ]*', '', definition).strip()
        definition = re.sub(' #.*', '', definition).strip()
        definition = re.sub('#1a.', '', definition).strip()
        definition = re.sub('@m.*', '', definition).strip('.').strip()
        return pos, definition

    @staticmethod
    def get_multiple_senses(description):
        lst = []
        for sense in unicode.split(description, '#1$D'):  # todo: sense without #5 is not sense  # nopep8
            def_and_pos = CollinsParser.separate_def_and_pos(sense)
            definition = def_and_pos[1]
            if not definition:
                continue
            pos = def_and_pos[0]
            lst.append({
                'definition': definition,
                'pos': pos})
        return lst

if __name__ == "__main__":
    CollinsParser.print_definitions(CollinsParser.parse_file(sys.argv[1]))
