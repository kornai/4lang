from tempfile import NamedTemporaryFile
import json
from ConfigParser import ConfigParser


class MagyarlancWrapper():

    def parse_sentences(self, entries):
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

    def run_magyarlanc(in_file, out_file):
        return_code = subprocess.call(['java', '-Xmx2G', '-jar',
            'magyarlanc-2.0.jar', '-mode', 'depparse', '-input', in_file,
            '-output', out_file, '-encoding', 'ISO-8859-2'])
        return return_code == 0

    def main():
        pass
