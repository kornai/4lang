import argparse
import os.path
import re

# Argument parser initialization
parser = argparse.ArgumentParser();
parser.add_argument("-w1", "--word1",
                    help="First word of wordpair to add.", type=str)
parser.add_argument("-w2", "--word2",
                    help="Second word of wordpair to add.", type=str)
args = parser.parse_args();

str_to_write = ''

if not os.path.exists('test/input/simlex_test.xml'):
    os.system("touch test/input/simlex_test.xml")

with open('test/input/simlex_test.xml', 'a+') as sim_test_file:
    existing_words = sim_test_file.readlines()

    with open('/home/recski/data/ldoce4/ldoce4_one_entry_per_line.xml', 'r') as f:
        content = f.readlines()
        re_str1 = '<HWD>\s+' + args.word1 + '\s+</HWD>'
        re_str2 = '<HWD>\s+' + args.word2 + '\s+</HWD>'
        for line in content:
            if re.search(re_str1, line):
                already_in = False
                if  not existing_words:
                    str_to_write += line
                else:
                    for line2 in existing_words:
                        if re.search(re_str1, line2):
                            already_in = True
                            break
                    if not already_in:
                        str_to_write += line
            if re.search(re_str2, line):
                already_in = False
                if  not existing_words:
                    str_to_write += line
                else:
                    for line2 in existing_words:
                        if re.search(re_str2, line2):
                            already_in = True
                            break
                    if not already_in:
                        str_to_write += line

    sim_test_file.write(str_to_write)