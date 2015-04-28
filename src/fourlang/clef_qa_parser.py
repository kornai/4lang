# parser for the input format of the Entrance Exam WA Task at CLEF2015
from HTMLParser import HTMLParser
import re

from xml_parser import XMLParser

class QAParser(XMLParser):

    html_parser = HTMLParser()

    answer_regex = re.compile('<answer a_id="([0-9]+)">(.*?)</answer>')
    question_regex = re.compile(
        '<question q_id="([0-9]+)">.*?<q_str>(.*?)</q_str>(.*?)</question>',
        re.S)
    doc_regex = re.compile('<doc d_id="([0-9]+)">(.*?)</doc>', re.S)
    test_regex = re.compile(
        '<reading-test r_id="([0-9]+)">(.*?)</reading-test>', re.S)
    topic_regex = re.compile(
        '<topic t_id="([0-9]+)" t_name="(.*?)">(.*?)</topic>', re.S)

    @staticmethod
    def get_questions(r_body):
        questions = []
        for q_id, q_str, q_body in QAParser.question_regex.findall(r_body):
            answers = [
                {"id": int(a_id), "answer": a_str.strip()}
                for a_id, a_str in QAParser.answer_regex.findall(q_body)]
            questions.append({"id": int(q_id), "question": q_str.strip(),
                              "answers": answers})
        return questions

    @staticmethod
    def get_tests(xml):
        for t_id, t_name, t_body in QAParser.topic_regex.findall(xml):
            for r_id, r_body in QAParser.test_regex.findall(t_body):
                docs = [
                    {"id": int(d_id),
                     "doc": QAParser.html_parser.unescape(d_body).strip()}
                    for d_id, d_body in QAParser.doc_regex.findall(r_body)]
                questions = QAParser.get_questions(r_body)
                yield {'t_id': int(t_id), 't_name': t_name, 'r_id': int(r_id),
                       'docs': docs, 'questions': questions}

    @staticmethod
    def parse_xml(xml):
        for test in QAParser.get_tests(xml):
            yield test

def test():
    import json
    import sys
    xml = sys.stdin.read()
    for entry in QAParser.parse_xml(xml):
        print json.dumps(entry)

if __name__ == "__main__":
    test()
