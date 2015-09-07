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
           for sense in section['senses']:
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

#   @staticmethod
#   def pattern_obj(pattern):
#       print "pattern_obj returns: " + str(type(re.compile(pattern, re.S)))
#       return re.compile(pattern, re.S)

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
       entry = re.sub('\n', ' ', entry)
       for pattern in ['#\+', '@\.', '\?!']:
           entry = re.sub(pattern, "", entry)
       for pattern in ['@n']:
           entry = re.sub(pattern, " ", entry)
       return {'hw': CollinsParser.get_hw(entry),
           'senses': CollinsParser.get_senses(entry)}

   @staticmethod
   def get_hw(entry):
       return re.search('(.+?)#[56]', entry, re.S).group(1)

   @staticmethod
   def get_senses(entry):
#       print 'Entry: ' + entry + '.'
       description = re.search('#[56](.+)', entry, re.S).group(1)
#       print 'Description: ' + description + '.'
       if '@n#1$D' in description:  # check multiple senses for word
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
       return lst_of_senses

   @staticmethod
   def get_mono_sense(description):
       return [{'definition': description}]

   @staticmethod
   def get_multiple_senses(description):
       lst = []
       is_first = True
       for sense in unicode.split(description, '@n#1$D'):
           if is_first:
#               print 'Sense: ' + sense + '.'
               if '#5' in sense:
                   if '#' not in re.findall('#5', sense)[-1]:  # ellenorizni
                        lst.append(re.findall('#5', sense)[-1])
           else:
               lst.append({'definition': sense})
           is_first = False
       return lst


if __name__ == "__main__":
    CollinsParser.print_definitions(CollinsParser.parse_file(sys.argv[1]))
