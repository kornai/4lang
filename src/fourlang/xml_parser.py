import re

class XMLParser():

    @staticmethod
    def section_pattern(tag):
        pattern_string = "<{0}>(.*?)</{0}>".format(tag)
        return re.compile(pattern_string, re.S)

    @staticmethod
    def tag_pattern(tag):
        pattern_string = "</?{0}>".format(tag)
        return re.compile(pattern_string, re.S)

    @staticmethod
    def iter_sections(tag, text):
        return XMLParser.section_pattern(tag).findall(text)

    @staticmethod
    def get_section(tag, text):
        match_obj = XMLParser.section_pattern(tag).search(text)
        return None if match_obj is None else match_obj.group(1)
    
    @staticmethod
    def remove_sections(tag, text):
        return XMLParser.section_pattern(tag).sub("", text)

    @staticmethod
    def remove_tags(tag, text):
        return XMLParser.tag_pattern(tag).sub("", text)
    
    @classmethod
    def parse_file(cls, fn):
        return cls.parse_xml(open(fn).read().decode('utf-8'))

