import json
import logging
import os
import subprocess
from tempfile import NamedTemporaryFile

from utils import ensure_dir

class StanfordWrapper():

    class ParserError(Exception):
        pass

    def __init__(self, cfg):
        self.cfg = cfg
        self.get_paths()

    def get_paths(self):
        stanford_dir = self.cfg.get('stanford', 'dir')
        parser_fn = self.cfg.get('stanford', 'parser')
        model_fn = self.cfg.get('stanford', 'model')
        self.parser_path = os.path.join(stanford_dir, parser_fn)
        self.model_path = os.path.join(stanford_dir, model_fn)
        if not (os.path.exists(self.parser_path) and
                os.path.exists(self.model_path)):
            raise Exception("cannot find parser and model files!")

        self.jython_path = self.cfg.get('stanford', 'jython')
        if not os.path.exists(self.jython_path):
            raise Exception("cannot find jython executable!")

        self.jython_module = os.path.join(
            os.path.dirname(__file__), "stanford_parser.py")

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

    def run_parser(self, in_file, out_file, definitions):
        return_code = subprocess.call([
            self.jython_path, self.jython_module, self.parser_path,
            self.model_path, in_file, out_file, str(int(definitions))])
        return return_code == 0

    def parse_sentences_old(self, sentences):
        """sentences should be a list of dictionaries, each with a "sen" key
        whose value will be parsed, a "deps" key whose value is a list for
        collecting dependencies, and a "pos" key that may map to constraints on
        the parse"""
        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as in_file:
            json.dump(sentences, in_file)
            in_file_name = in_file.name
        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as out_file:
            success = self.run_parser(in_file_name, out_file.name)
            if not success:
                logging.critical(
                    "jython returned non-zero exit code, aborting")
                raise StanfordWrapper.ParserError()
            parsed_sentences = json.load(out_file)
        sentences.update(parsed_sentences)
        return True

    def parse_sentences(self, entries, definitions=False):
        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as in_file:
            json.dump(entries, in_file)
            in_file_name = in_file.name

        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as out_file:
            out_file_name = out_file.name
            success = self.run_parser(in_file_name, out_file_name, definitions)

        if not success:
            logging.critical(
                "jython returned non-zero exit code, aborting")
            raise StanfordWrapper.ParserError()

        with open(out_file_name) as out_file:
            new_entries = json.load(out_file)

        return new_entries
