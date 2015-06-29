import logging
import sys

import nltk.data

from clef_qa_parser import QAParser
from similarity import WordSimilarity
from text_to_4lang import TextTo4lang
from utils import get_cfg

__LOGLEVEL__ = 'INFO'

class QuestionAnswerer:
    def __init__(self, cfg):
        self.cfg = cfg

        nltk.download('punkt', quiet=True)
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.text_to_4lang = TextTo4lang(cfg)
        self.word_similarity = WordSimilarity(cfg)

    def score_answer(self, answer, model):
        known_words = set(answer.keys()) & set(model.keys())
        score = 0
        for word in known_words:
            w_sim = self.word_similarity.machine_similarity(
                answer[word], model[word], 'default')
            score += w_sim

        return score / float(len(known_words))

    def answer_question(self, question, model):
        logging.info('processing question: {0}...'.format(question['text']))
        question['machines'] = self.text_to_4lang.process(question['text'])
        for answer in question['answers']:
            logging.info('processing answer: {0}...'.format(answer['text']))
            answer['machines'] = self.text_to_4lang.process(answer['text'])
            answer['score'] = self.score_answer(answer['machines'], model)
            logging.info('score: {0}...'.format(answer['score']))

        top_answer = sorted(question['answers'], key=lambda a: -a['score'])[0]
        return top_answer

    def run(self):
        logging.info('running QA...')
        input_file = self.cfg.get('qa', 'input_file')
        for entry in QAParser.parse_file(input_file):
            logging.info('processing text...')
            sens = []
            for doc in entry['docs']:
                sens += self.sent_detector.tokenize(doc['text'])

            model = self.text_to_4lang.process(sens)

            for question in entry['questions']:
                answer = self.answer_question(question, model)
                print answer

    def answer_questions(self):
        for question in self.questions:

            self.answer_question(question)

def main():
    logging.basicConfig(
        level=__LOGLEVEL__,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = get_cfg(cfg_file)
    qa = QuestionAnswerer(cfg)
    qa.run()

if __name__ == "__main__":
    main()
