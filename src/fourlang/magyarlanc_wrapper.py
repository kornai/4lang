from subprocess import Popen, PIPE


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
        print 'first_run set to True'

    def parse_sentences(self, entries):
        print 'entries: ' + str(entries)
        print 'type of entries: ' + str(type(entries))
        for entry in entries:
            for sense in entry['senses']:
                df = sense['definition']
                sense['definition'] = {'sen': df, 'deps': self.tag(df)}
                yield entry

    def read_header(self):
        for i in xrange(13):
            print self._process.stdout.readline().strip()

    def tag(self, sentence):
        print u'sentence: {0}'.format(sentence).encode('utf-8')
        self._process.stdin.write(sentence.encode('utf-8') + "\n")
        self._process.stdin.flush()

        if self.first_run:
            self.read_header()
            self.first_run = False
            print 'first_run set to False'

        self.deps = []
        line = self._process.stdout.readline().strip()
        while line:
#            yield self.convert_dep(line)
            self.convert_deps(line)
            line = self._process.stdout.readline().strip()
        print 'deps: ' + repr(self.deps)
        self.modify_deps()
        print 'modified_deps: ' + repr(self.modified_deps)
        return self.modified_deps

    def convert_deps(self, line):
        print 'line: ' + line
        line = line.split()
        self.deps.append({
            'num': line[0], 'word': line[1], 'pair': line[6], 'type': line[7]})

    def modify_deps(self):
#        self.modified_deps = self.deps
        self.modified_deps = []
        for line in self.deps:
            print 'next line'
            print 'type: ' + line['type']
            print 'word: ' + line['word']
            print 'num: ' + line['num']
            print 'pair: ' + line['pair']
            self.modified_deps.append(line['type'].lower() + '(' + line['word'] + '-' + line['num'] + ', ' + self.get_pair_word(line['pair']) + '-' + line['pair'] + ')')

    def get_pair_word(self, pair):
        for line in self.deps:
            if line['num'] == pair:
                print 'pair word: ' + line['word']
                return line['word']
        return 'ROOT'


def test():
    import sys
    from utils import get_cfg
    cfg = get_cfg(sys.argv[1])
    m = Magyarlanc(cfg)
    test_sens = ["Egy", "Hat", "Nyolc"]
    for sen in test_sens:
        for line in m.tag(sen):
            print line

if __name__ == '__main__':
    test()
