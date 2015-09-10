from tempfile import NamedTemporaryFile
import json
import subprocess
from ConfigParser import ConfigParser
from utils import ensure_dir


class MagyarlancWrapper():

    def __init__(self, cfg):
        self.cfg = cfg

    def parse_sentences(self, entries):

        self.tmp_dir = self.cfg.get('data', 'tmp_dir')
        ensure_dir(self.tmp_dir)

        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as in_file:
            json.dump(entries, in_file)
            in_file_name = in_file.name

        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as out_file:
            out_file_name = out_file.name
            success = self.run_magyarlanc(in_file_name, out_file_name)

        if success:
            print 'magyarlanc ok'
        else:
            print 'magyarlanc nem ok'

        with open(out_file_name) as out_file:
            new_entries = json.load(out_file)

        return new_entries

    def run_magyarlanc(self, in_file, out_file):
        return_code = subprocess.call([
            'java', '-Xmx2G', '-jar', 'magyarlanc/magyarlanc-2.0.jar',
            '-mode', 'depparse', '-input', in_file,
            '-output', out_file, '-encoding', 'ISO-8859-2'])
        return return_code == 0

    def main():
        pass
