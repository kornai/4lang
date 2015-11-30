import logging
import sys

from pymachine.utils import MachineGraph

from clef_qa_parser import QAParser
from similarity import GraphSimilarity, WordSimilarity
from text_to_4lang import TextTo4lang
from utils import ensure_dir, get_cfg, print_text_graph

__LOGLEVEL__ = 'INFO'

class QuestionAnswerer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.text_to_4lang = TextTo4lang(cfg)
        self.graph_dir = self.cfg.get("qa", "graph_dir")
        self.dep_dir = self.cfg.get("qa", "deps_dir")
        ensure_dir(self.graph_dir)
        ensure_dir(self.dep_dir)
        self.word_similarity = WordSimilarity(cfg)

    def score_answer(self, answer, model, model_graph):
        answer_graph = MachineGraph.create_from_machines(
            answer['machines'].values())
        answer['score'], answer['evidence'] = GraphSimilarity.supported_score(
            answer_graph, model_graph)

    def old_score_answer(self, answer, model):
        machines = answer['machines']
        known_words = set(machines.keys()) & set(model.keys())
        answer['evidence'] = []
        word_sims = dict((
            (word, self.word_similarity.machine_similarity(
                machines[word], model[word], 'default'))
            for word in known_words))

        answer['score'] = sum(word_sims.values()) / float(len(machines))
        answer['evidence'] = sorted(
            [(score, word) for word, score in word_sims.iteritems() if score],
            reverse=True)

    def answer_question(self, question, model, model_graph):
        logging.info('processing question: {0}...'.format(question['text']))
        question['machines'] = self.text_to_4lang.process(
            question['text'], dep_dir=self.dep_dir,
            fn="q{0}".format(question['id']))

        for answer in question['answers']:
            logging.info('processing answer: {0}...'.format(answer['text']))
            answer['machines'] = self.text_to_4lang.process(
                answer['text'], dep_dir=self.dep_dir,
                fn="q{0}a{1}".format(question['id'], answer['id']))
            print_text_graph(
                answer['machines'], self.graph_dir, fn="q{0}a{1}".format(
                    question['id'], answer['id']))
            self.score_answer(answer, model, model_graph)
            logging.info('score: {0}, evidence: {1}'.format(
                answer['score'], answer['evidence']))

        top_answer = sorted(question['answers'], key=lambda a: -a['score'])[0]
        return top_answer

    def run(self):
        logging.info('running QA...')
        input_file = self.cfg.get('qa', 'input_file')
        for entry in QAParser.parse_file(input_file):
            logging.info('processing text...')
            all_text = "\n".join([doc['text'] for doc in entry['docs']])
            model = self.text_to_4lang.process(
                all_text, dep_dir=self.dep_dir, fn='text')
            print_text_graph(model, self.graph_dir)
            model_graph = MachineGraph.create_from_machines(model.values())
            for question in entry['questions']:
                answer = self.answer_question(question, model, model_graph)
                print answer['text']

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
