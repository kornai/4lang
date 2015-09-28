from subprocess import Popen, PIPE
import logging


class Magyarlanc():
    def __init__(self, cfg):
        jar_path = cfg.get('magyarlanc', 'dir')
        self.runnable = 'java'
        self.options = [
            '-Xmx2G', '-jar', jar_path, '-mode', 'depparse-service']
        self._process = Popen([self.runnable] + self.options,
                              stdin=PIPE, stdout=PIPE, stderr=PIPE)

        self.lines_iterator = iter(self._process.stdout.readline, b"")
        self.first_run = True
        # print 'first_run set to True'

    def parse_sentences(self, entries):
        # print 'entries: ' + str(entries)
        # print 'type of entries: ' + str(type(entries))
        logging.info('parsing...')
        count = 0
        for entry in entries:
            count += 1
            if count % 100 == 0:
                logging.info(str(count))
            for sense in entry['senses']:
                df = sense['definition']
                sense['definition'] = {'sen': df, 'deps': self.tag(df)}
                yield entry
        logging.info(str(count))

    def read_header(self):
        for i in xrange(13):
            logging.info(self._process.stdout.readline().strip())

    def tag(self, sentence):
        # print u'sentence: {0}'.format(sentence).encode('utf-8')
        self._process.stdin.write(sentence.encode('utf-8') + "\n")
        self._process.stdin.flush()

        if self.first_run:
            self.read_header()
            self.first_run = False
            # print 'first_run set to False'

        deps = {'0': {"word": "ROOT"}}
        line = self._process.stdout.readline().strip()
        while line:
            # yield self.convert_dep(line)
            self.add_deps(line, deps)
            line = self._process.stdout.readline().strip()
        # print 'deps: ' + repr(self.deps)
        dep_strings = self.deps_to_strings(deps)
        # print 'modified_deps: ' + repr(self.modified_deps)
        return dep_strings

    def add_deps(self, line, deps):
        # print 'line: ' + line
        l = line.split()
        deps[l[0]] = {'word': l[1], 'pair': l[6], 'type': l[7]}

    def deps_to_strings(self, deps):
        # self.modified_deps = self.deps
        dep_strings = []
        for num, dep in deps.iteritems():
            # print 'next line'
            # print 'type: ' + line['type']
            # print 'word: ' + line['word']
            # print 'num: ' + line['num']
            # print 'pair: ' + line['pair']
            if num == '0':
                continue
            pair = deps[dep['pair']]
            dep_strings.append("{0}({1}-{2}, {3}-{4})".format(
                dep['type'].lower(), dep['word'], num,
                pair['word'], dep['pair']))
        return dep_strings

    def get_pair_word(self, pair):
        for line in self.deps:
            if line['num'] == pair:
                # print 'pair word: ' + line['word']
                return line['word']
        return 'ROOT'


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
