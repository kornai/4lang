from ConfigParser import ConfigParser
import json
import logging
import os
import requests
import subprocess
from subprocess import Popen, PIPE
import sys
from tempfile import NamedTemporaryFile

from utils import ensure_dir

class StanfordWrapper():

    http_request_headers = {
        'Content-type': 'application/json', 'Accept': 'text/plain'}

    class ParserError(Exception):
        pass

    def __init__(self, cfg, is_server=False):
        self.cfg = cfg
        remote = self.cfg.getboolean('stanford', 'remote')
        if is_server or not remote:
            self.get_stanford_paths()
            if is_server:
                # used as server
                self.start_parser()
                self.parse_sentences = self.parse_sentences_server
            else:
                # standalone, using jython
                self.get_jython_paths()
                self.parse_sentences = self.parse_sentences_local
        else:
            # used as client
            self.server_url = self.cfg.get('stanford', 'url')
            self.parse_sentences = self.parse_sentences_remote

    def get_stanford_paths(self):
        self.stanford_dir = self.cfg.get('stanford', 'dir')
        parser_fn = self.cfg.get('stanford', 'parser')
        self.model_fn = self.cfg.get('stanford', 'model')
        self.parser_path = os.path.join(self.stanford_dir, parser_fn)
        self.model_path = os.path.join(self.stanford_dir, self.model_fn)
        if not (os.path.exists(self.parser_path) and
                os.path.exists(self.model_path)):
            raise Exception("cannot find parser and model files!")

    def get_jython_paths(self):
        self.jython_path = self.cfg.get('stanford', 'jython')
        if not os.path.exists(self.jython_path):
            raise Exception("cannot find jython executable!")

        self.jython_module = os.path.join(
            os.path.dirname(__file__), "stanford_parser.py")

        self.tmp_dir = self.cfg.get('data', 'tmp_dir')
        ensure_dir(self.tmp_dir)

    def start_parser(self):
        command = [
            'java', '-mx1500m', '-cp', '{0}/*:'.format(self.stanford_dir),
            'edu.stanford.nlp.parser.lexparser.LexicalizedParser',
            '-outputFormat', 'collapsedDependencies',
            '-sentences', 'newline',
            'edu/stanford/nlp/models/lexparser/{0}'.format(self.model_fn),
            '-']

        logging.info(
            "starting stanford parser with this command: {0}".format(
                ' '.join(command)))

        self.parser_process = Popen(command, stdin=PIPE, stdout=PIPE)

    def parse_sentences_server(self, sens, definitions=False):
        parsed_sens = []
        for c, sentence in enumerate(sens):
            parsed_sens.append({'sen': sentence, 'deps': []})
            # logging.info('writing to stdin...')
            self.parser_process.stdin.write(sentence+'\n')
            self.parser_process.stdin.flush()
            # logging.info('reading from stdout...')
            line = self.parser_process.stdout.readline().strip()
            while line:
                # logging.info('read this: {0}'.format(repr(line)))
                if line == '':
                    break
                parsed_sens[-1]['deps'].append(line.strip())
                line = self.parser_process.stdout.readline().strip()

        # logging.info('returning parsed sens')
        return parsed_sens

    def create_input_file(self, sentences, token):
        sen_file = NamedTemporaryFile(
            dir=self.tmp_dir, prefix=token, delete=False)
        for sen in sentences:
            #  need to add a period so the Stanford Parser knows where
            #  sentence boundaries are. There should be a smarter way...
            sen_file.write(
                u"{0}\n".format(sen['sen']).encode('utf-8'))

        return sen_file.name

    def run_parser(self, in_file, out_file, definitions):
        return_code = subprocess.call([
            self.jython_path, self.jython_module, self.parser_path,
            self.model_path, in_file, out_file, str(int(definitions)),
            str(logging.getLogger(__name__).getEffectiveLevel())])
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

    def parse_sentences_remote(self, entries, definitions=False):
        req = requests.get(
            self.server_url, data=json.dumps(entries),
            headers=StanfordWrapper.http_request_headers)

        return json.loads(req.text)

    def parse_sentences_local(self, entries, definitions=False):
        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as in_file:
            json.dump(entries, in_file)
            in_file_name = in_file.name
        logging.info("dumped input to {0}".format(in_file_name))

        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as out_file:
            out_file_name = out_file.name
            logging.info("writing parses to {0}".format(out_file_name))
            success = self.run_parser(in_file_name, out_file_name, definitions)

        if not success:
            logging.critical(
                "jython returned non-zero exit code, aborting")
            raise StanfordWrapper.ParserError()

        logging.debug("reading output...")
        with open(out_file_name) as out_file:
            new_entries = json.load(out_file)

        return new_entries

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")

    from flask import Flask, request, Response

    cfg_file = 'conf/default.cfg' if len(sys.argv) < 2 else sys.argv[1]
    cfg = ConfigParser()
    cfg.read([cfg_file])

    wrapper = StanfordWrapper(cfg, is_server=True)

    app = Flask(__name__)

    @app.route("/")
    def hello():
        sens = request.get_json()
        # logging.info('got this: {0}'.format(sens))
        parsed_sens = wrapper.parse_sentences(sens)
        # logging.info('returning response...')
        # logging.info('returning this: {0}'.format(parsed_sens))
        return Response(json.dumps(parsed_sens), mimetype='application/json')

    app.run()
