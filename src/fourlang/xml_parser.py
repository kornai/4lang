import re

class XMLParser():

    @staticmethod
    def section_pattern(tag):
        """Create (section) regex object."""
        pattern_string = "<{0}>(.*?)</{0}>".format(tag)
        return re.compile(pattern_string, re.S)  # S: . can be newline

    @staticmethod
    def tag_pattern(tag):
        """Create (tag) regex object."""
        pattern_string = "</?{0}>".format(tag)
        return re.compile(pattern_string, re.S)

    @staticmethod
    def iter_sections(tag, text):
        """Return list of tags in text."""
        return XMLParser.section_pattern(tag).findall(text)

    @staticmethod
    def get_section(tag, text):
        """Return the first group of tag in text."""
        match_obj = XMLParser.section_pattern(tag).search(text)
        return None if match_obj is None else match_obj.group(1)

    @staticmethod
    def remove_sections(tag, text):
        """Remove (section) tags from text."""
        return XMLParser.section_pattern(tag).sub("", text)

    @staticmethod
    def remove_tags(tag, text):
        """Remove (tag) tags from text."""
        return XMLParser.tag_pattern(tag).sub("", text)

    @staticmethod
    def parse_xml(data):
        raise NotImplementedError

    @classmethod
    def parse_file(cls, fn):
        """Open, read and decode the input file,
        then give it to the main parser class' 'parse_xml' method."""
        return cls.parse_xml(open(fn).read().decode('utf-8'))
