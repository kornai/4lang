import logging
import os
import sys
import threading
import time

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
        no_files_written = 0
        out_file = None
        for out_line in os.popen(command):
            if out_line == '\n':
                out_file.close()
                no_files_written += 1
                out_file = None
                continue

            if out_file is None:
                out_file = open(os.path.join(
                    out_dir, "{0}.dep".format(
                        word_list[no_files_written])), "w")
            out_file.write(out_line)

        if out_file is not None:
            out_file.close()
            no_files_written += 1

        if len(file_list) != no_files_written:
            raise Exception(
                "# of input and output files don't match ({0} vs {1})".format(
                    len(file_list), no_files_written))

    def parse_all_files_thread(self, i, file_list, out_dir, files_per_batch):
        try:
            for batch in batches(file_list, files_per_batch):
                self.parse_files(batch, out_dir)
            self.thread_states[i] = True
        except Exception as e:
            logging.warning("parse failed on thread {0}".format(i))
            self.thread_states[i] = False
            raise Exception(e)

    def parse_all_files(self, in_dir, out_dir, no_threads=1,
                        files_per_batch=1000):
        file_list = [os.path.join(in_dir, fn) for fn in os.listdir(in_dir)]
        files_per_thread = (len(file_list) / no_threads) + 1
        self.thread_states = {}
        for i, batch in enumerate(batches(file_list, files_per_thread)):
            t = threading.Thread(target=self.parse_all_files_thread,
                                 args=(i, batch, out_dir, files_per_batch))
            t.start()
        logging.info("started {0} threads".format(no_threads))
        while True:
            if len(self.thread_states) < no_threads:
                time.sleep(1)
                continue
            elif all(self.thread_states.values()):
                logging.info(
                    "{0} threads finished successfully".format(no_threads))
            else:
                logging.info("some threads failed")
            break

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    in_dir, out_dir = sys.argv[1:3]
    no_threads = int(sys.argv[3])
    stanford_wrapper = StanfordWrapper()
    stanford_wrapper.parse_all_files(in_dir, out_dir, no_threads=no_threads)

if __name__ == '__main__':
    main()
