import subprocess
from tempfile import NamedTemporaryFile
import logging
import sys
import traceback

class Magyarlanc():
    def __init__(self, cfg):
        self.path = cfg.get('magyarlanc', 'path')
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
        with NamedTemporaryFile(dir=self.tmp_dir, delete=False) as out_file:
            return_code = subprocess.call([
                'java', '-Xmx2G', '-jar', self.path,
                '-mode', 'depparse', '-input', in_file_name,
                '-output', out_file.name])
            if return_code == 0:
                return out_file.name
            return None

    def parse_lines(self, lines):
        id_to_toks = {"0": {"lemma": "ROOT", "tok": "ROOT", "msd": None}}
        for line in lines:
            i, tok, lemma, msd, _, __, gov, dep = line.strip().split('\t')
            id_to_toks[i] = {
                'tok': tok, 'lemma': lemma, 'msd': msd, 'gov': gov, 'dep': dep}
        deps = []
        for i, t in id_to_toks.iteritems():
            if t['lemma'] == 'ROOT':
                continue
            gov = id_to_toks[t['gov']]
            deps.append({
                "type": t['dep'].lower(),
                "gov": {
                    'id': t['gov'], "word": gov['tok'], "lemma": gov['lemma'],
                    'msd': gov['msd']
                },
                "dep": {
                    'id': i, "word": t['tok'], "lemma": t['lemma'],
                    'msd': t['msd']
                }
            })

        return deps

    def add_deps(self, entry, lines):
        entry['senses'][0]['definition'] = {
            "sen": entry['senses'][0]['definition'],
            "deps": self.parse_lines(lines)}

    def parse_text(self, text):
        in_file_name = self.dump_text(text)
        raw_parses = self.parse_file(in_file_name)
        return self.parse_magyarlanc_output(raw_parses)

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
