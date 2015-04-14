from collections import defaultdict
import re

class Dependencies():
    dep_regex = re.compile("([a-z_-]*)\((.*?)-([0-9]*)'*, (.*?)-([0-9]*)'*\)")

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

    def get_dep_list(self):
        dep_list = []
        for word1, (dependants, _) in self.index.iteritems():
            for dep, words in dependants.iteritems():
                for word2 in words:
                    dep_list.append((dep, word1, word2))
        return dep_list

class DependencyProcessor():
    copulars = set([
        "'s", 'are', 'be', 'been', 'being', 'is', 's', 'was', 'were'])

    def __init__(self, cfg):
        self.cfg = cfg

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

    def process_dependencies(self, dep_strings):
        deps = Dependencies.create_from_strings(dep_strings)
        deps = self.process_copulars(deps)
        deps = self.remove_copulars(deps)
        return deps.get_dep_list()
