from subprocess import Popen, PIPE


class Magyarlanc():
    def __init__(self, jar_path):
        self.runnable = 'java'
        self.options = [
            '-Xmx2G', '-jar', jar_path, '-mode', 'depparse-service']
        self._process = Popen([self.runnable] + self.options,
                              stdin=PIPE, stdout=PIPE, stderr=PIPE)

        self.lines_iterator = iter(self._process.stdout.readline, b"")
        self.first_run = True

    def read_header(self):
        for i in xrange(13):
            print self._process.stdout.readline().strip()

    def tag(self, sentence):
        self._process.stdin.write(sentence.encode('utf-8') + "\n")
        self._process.stdin.flush()
        if self.first_run:
            self.read_header()
            self.first_run = False

        line = self._process.stdout.readline().strip()
        while line:
            yield line
            line = self._process.stdout.readline().strip()

def test():
    import sys
    m = Magyarlanc(sys.argv[1])
    test_sens =  ["Egy", "Hat", "Nyolc"]
    for sen in test_sens:
        for line in m.tag(sen):
            print line

if __name__ == '__main__':
    test()
