import ijson
import json
import logging
import sys


class WikiData():

    @staticmethod
    def item_iterator(fn):
        with open(fn) as f:
            f.readline()  # '['
            for line in f:
                raw_json = line.rstrip('\n').rstrip(',')
                item = json.loads(raw_json)
                yield item

    def __init__(self, fn):
        self.fn = fn

    def labels(self, lang, n=10000):
        c = 0
        for item in WikiData.item_iterator(self.fn):
            c += 1
            if c > n:
                return
            if c % 10000 == 0:
                logging.info("{0}K".format(c/1000))
            label = item['labels'].get(lang)
            if label is None:
                yield None
            else:
                yield label['value']


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    fn = sys.argv[1]
    wd = WikiData(fn)
    labels = list(wd.labels('en'))
    filtered_labels = filter(None, labels)
    print '#items: {0}, #labels: {1}'.format(len(labels), len(filtered_labels))

if __name__ == "__main__":
    main()
