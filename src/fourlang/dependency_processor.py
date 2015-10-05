from collections import defaultdict
from copy import deepcopy
import logging
import re

class Dependencies():
    dep_regex = re.compile("(.*?)\((.*?)-([0-9]*)'*, (.*?)-([0-9]*)'*\)")

    @staticmethod
    def parse_dependency(string):
        dep_match = Dependencies.dep_regex.match(string)
        if not dep_match:
            raise Exception('cannot parse dependency: {0}'.format(string))
        dep, word1, id1, word2, id2 = dep_match.groups()
        return dep, (word1, id1), (word2, id2)

    @staticmethod
    def create_from_strings(dep_strings):
        dep_list = map(Dependencies.parse_dependency, dep_strings)
        return Dependencies(dep_list)

    def __init__(self, dep_list):
        self.dep_list = dep_list
        self.index_dependencies(dep_list)

    def index_dependencies(self, deps):
        self.index = defaultdict(lambda: (defaultdict(set), defaultdict(set)))
        for triple in deps:
            self.add(triple)

    def remove(self, (dep, word1, word2)):
        self.index[word1][0][dep].remove(word2)
        self.index[word2][1][dep].remove(word1)

    def add(self, (dep, word1, word2)):
        self.index[word1][0][dep].add(word2)
        self.index[word2][1][dep].add(word1)

    def get_dep_list(self, exclude=[]):
        dep_list = []
        for word1, (dependants, _) in self.index.iteritems():
            for dep, words in dependants.iteritems():
                if any(dep.startswith(patt) for patt in exclude):
                    continue
                for word2 in words:
                    dep_list.append((dep, word1, word2))
        return dep_list

    def get_root(self):
        root_words = self.index[(u'ROOT', u'0')][0]['root']
        if len(root_words) != 1:
            logging.warning('no unique root element: {0}'.format(root_words))
            return None
        return iter(root_words).next()

    def merge(self, word1, word2, exclude=[]):
        for dep, w1, w2 in self.get_dep_list(exclude=exclude):
            if w1 in (word1, word2) and w2 in (word1, word2):
                pass
            elif w1 == word1:
                self.add((dep, word2, w2))
            elif w1 == word2:
                self.add((dep, word1, w2))
            elif w2 == word1:
                self.add((dep, w1, word2))
            elif w2 == word2:
                self.add((dep, w1, word1))
            else:
                pass

class DependencyProcessor():
    copulars = set([
        "'s", 'are', 'be', 'been', 'being', 'is', 's', 'was', 'were'])

    def __init__(self, cfg):
        self.cfg = cfg

    def process_coordination(self, deps):
        for word1, word_deps in deepcopy(deps.index.items()):
            for i in (0, 1):
                for dep, words in word_deps[i].iteritems():
                    if dep.startswith('conj_'):
                        for word2 in words:
                            deps.merge(word1, word2, exclude=['conj_'])
        return deps

    def process_coordinated_root(self, deps):
        root_word = deps.get_root()
        for i in (0, 1):
            for dep, words in deepcopy(deps.index[root_word][i]).iteritems():
                if dep.startswith('conj_'):
                    for word in words:
                        deps.merge(word, root_word, exclude=['conj_'])
        return deps

    def process_rcmods(self, deps):
        # rcmods = [
        #     (w1, w2) for w1, (dependants, _) in deps.index.iteritems()
        #     for dep, words in dependants.iteritems()
        #     for w2 in words if dep == 'rcmod']
        return deps

    def process_copulars(self, deps):
        # rcmod(x, is), prep_P(is, y) -> prep_P(x, y)
        copulars = [(word, w_id) for word, w_id in deps.index.iterkeys()
                    if word in DependencyProcessor.copulars]
        new_deps = []
        for cop in copulars:
            if 'rcmod' in deps.index[cop][1]:
                for dep, words in deps.index[cop][0].iteritems():
                    if dep.startswith('prep_'):
                        for word2 in words:
                            new_deps += [
                                (dep, word3, word2)
                                for word3 in deps.index[cop][1]['rcmod']]
        for new_dep in new_deps:
            # logging.info('adding new dep: {0}'.format(new_dep))
            deps.add(new_dep)
        return deps

    def remove_copulars(self, deps):
        for dep, word1, word2 in deps.get_dep_list():
            if (word1[0] in DependencyProcessor.copulars or
                    word2[0] in DependencyProcessor.copulars):
                deps.remove((dep, word1, word2))

        return deps

    def process_string_dependencies(self, dep_strings):
        return self.process_dependencies(
            Dependencies.create_from_strings(dep_strings))

    def process_dependencies(self, deps):
        deps = self.process_copulars(deps)
        deps = self.remove_copulars(deps)
        deps = self.process_rcmods(deps)
        # deps = self.process_coordinated_root(deps)
        deps = self.process_coordination(deps)

        return deps.get_dep_list()
