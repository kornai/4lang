
import os
from tempfile import NamedTemporaryFile

from utils import ensure_dir

class StanfordWrapper():
    def __init__(self, cfg):
        self.cfg = cfg
        self.stanford_dir = self.cfg.get('stanford', 'stanford_dir')
        self.tmp_dir = self.cfg.get('data', 'tmp_dir')
        ensure_dir(self.tmp_dir)

    def create_input_file(self, sentences, token):
        sen_file = NamedTemporaryFile(
            dir=self.tmp_dir, prefix=token, delete=False)
        for sen in sentences:
            # need to add a period so the Stanford Parser knows where
            # sentence boundaries are. There should be a smarter way...
            sen_file.write(
                u"{0}\n".format(sen['sen']).encode('utf-8'))

        return sen_file.name

    def get_command(self, input_file_name):
        return 'java -mx150m -cp "{0}/*:" \
            edu.stanford.nlp.parser.lexparser.LexicalizedParser \
            -outputFormat "typedDependencies" -sentences newline \
            edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz {1}'.format(
            self.stanford_dir, input_file_name)

    def parse_sentences(self, sentences, token=""):
        """sentences should be a list of dictionaries, each with a "sen" key
        whose value will be parsed and a "deps" key whose value is a list for
        collecting dependencies"""
        input_file_name = self.create_input_file(sentences, token)
        command = self.get_command(input_file_name)

        sens_parsed = 0

        for out_line in os.popen(command):
            if out_line == '\n':
                sens_parsed += 1
                continue

            sentences[sens_parsed]['deps'].append(out_line.strip())

        if len(sentences) - sens_parsed not in (0, 1):
            raise Exception(
                "# of input and output sentences don't match" +
                "({0} vs {1})".format(len(sentences), sens_parsed))

        os.remove(input_file_name)
