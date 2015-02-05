import os
import sys

def batches(l, n):
    """ Yield successive n-sized chunks from l.
    (source: http://stackoverflow.com/questions/312443/
    how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class StanfordWrapper():
    stanford_dir = "/home/recski/projects/stanford_dp/stanford-parser-full-2014-08-27/"  # nopep8

    def parse_files(self, file_list, out_dir):
        word_list = [fn.split('/')[-1].split('.')[0] for fn in file_list]

        command = "{0}/lexparser_dep.sh {1}".format(
            StanfordWrapper.stanford_dir, " ".join(file_list))
        file_index = 0
        out_file = None
        for out_line in os.popen(command):
            if out_line == '\n':
                out_file.close()
                out_file = None
                file_index += 1
                continue

            if out_file is None:
                out_file = open(os.path.join(
                    out_dir, "{0}.dep".format(word_list[file_index])), "w")
            out_file.write(out_line)

    def parse_all_files(self, in_dir, out_dir, files_per_batch=1000):
        file_list = [os.path.join(in_dir, fn) for fn in os.listdir(in_dir)]
        for batch in batches(file_list, files_per_batch):
            self.parse_files(batch, out_dir)

def main():
    in_dir, out_dir = sys.argv[1:3]
    stanford_wrapper = StanfordWrapper()
    stanford_wrapper.parse_all_files(in_dir, out_dir)

if __name__ == '__main__':
    main()
