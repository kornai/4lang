import logging
import os
import subprocess
from StringIO import StringIO
import sys
from tempfile import NamedTemporaryFile
import traceback

from hunmisc.corpustools.tsv_tools import sentence_iterator, get_dependencies


class Magyarlanc():
    def __init__(self, cfg):
        self.jarpath = cfg.get('magyarlanc', 'jar')
        self.magyarlanc_dir = cfg.get('magyarlanc', 'dir')
        self.tmp_dir = cfg.get('data', 'tmp_dir')

    def dump_entries(self, entries):
        logging.info('dumping to file...')
        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as in_file:
            for e in entries:
                definition = e['senses'][0]['definition']
                definition = definition.replace('i. e.', 'i.e.')  # TODO
                in_file.write(u"{0}\n".format(definition).encode('utf-8'))
                in_file_name = in_file.name
        logging.info("dumped input to {0}".format(in_file_name))
        return in_file_name

    def dump_text(self, text):
        logging.info('dumping to file...')
        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as in_file:
            t = text.replace('i. e.', 'i.e.')  # TODO
            in_file.write(t.encode('utf-8'))
            in_file_name = in_file.name
        logging.info("dumped input to {0}".format(in_file_name))
        return in_file_name

    def run_parser(self, in_file_name):
        os.chdir(self.magyarlanc_dir)
        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as out_file:
            return_code = subprocess.call([
                'java', '-Xmx2G', '-jar', self.jarpath,
                '-mode', 'depparse', '-input', in_file_name,
                '-output', out_file.name])
            if return_code == 0:
                return out_file.name
            return None

    @staticmethod
    def lines_to_deps(lines):
        text_str = u"\n".join((u"".join(sen) for sen in list(lines)))
        tsv_stream = StringIO(text_str)
        return map(get_dependencies, sentence_iterator(tsv_stream))

    def add_deps(self, entry, lines):
        deps = Magyarlanc.lines_to_deps([lines])[0]
        entry['senses'][0]['definition'] = {
            "sen": entry['senses'][0]['definition'],
            "deps": deps}

    def parse_text(self, text):
        in_file_name = self.dump_text(text)
        raw_parses = self.parse_file(in_file_name)
        deps = Magyarlanc.lines_to_deps(raw_parses)
        return deps, []

    def parse_entries(self, entries):
        in_file_name = self.dump_entries(entries)
        raw_parses = self.parse_file(in_file_name)
        for count, parse in enumerate(raw_parses):
            try:
                self.add_deps(entries[count], parse)
            except:
                logging.error("count: {0}".format(count))
                logging.error("last entry: {0}".format(entries[count-1]))
                logging.error(u"failed with: {0}".format(parse))
                traceback.print_exc()
                sys.exit(-1)
        return entries

    def parse_file(self, in_file_name):
        logging.info('parser input: {0}'.format(in_file_name))
        out_file_name = self.run_parser(in_file_name)
        logging.info('parser output: {0}'.format(out_file_name))
        if out_file_name is None:
            logging.error('parser failed')
            sys.exit(-1)
        count = 0
        curr_lines = []
        for line in open(out_file_name):
            if line == '\n':
                yield curr_lines
                curr_lines = []
                count += 1
            else:
                curr_lines.append(line.decode('utf-8'))


def test():
    import sys
    from utils import get_cfg
    cfg = get_cfg(sys.argv[1])
    m = Magyarlanc(cfg)
    test_sens = ["valamely asztalon vagy padon az ablakra illesztett keret"]
    # test_sens = ["Egy", "Hat", "Nyolc"]
    for sen in test_sens:
        for line in m.tag(sen):
            print line

if __name__ == '__main__':
    test()
