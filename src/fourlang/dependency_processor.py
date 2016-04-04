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
        deps = [(dep, tuple(w1), tuple(w2)) for dep, w1, w2 in deps]
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


class NewDependencies():

    @staticmethod
    def create_from_old_deps(old_deps):
        deps = []
        for d_type, gov, dep in old_deps.get_dep_list():
            deps.append({
                "type": d_type,
                "gov": {
                    "word": gov[0],
                    "id": gov[1]},
                "dep": {
                    "word": dep[0],
                    "id": dep[1]}})
        return NewDependencies(deps)

    def __init__(self, deps):
        self.deps = deps
        self.indexed = False
        self.index()

    def index(self):
        self.tok_index = defaultdict(lambda: [None, [], []])
        self.dep_index = defaultdict(list)
        for d in self.deps:
            self.tok_index[d['gov']['id']][0] = d['gov']
            self.tok_index[d['dep']['id']][0] = d['dep']
            self.tok_index[d['gov']['id']][1].append(d)
            self.tok_index[d['dep']['id']][2].append(d)
            self.dep_index[d['type']].append(d)

        self.indexed = True

    def add(self, d_type, gov, dep):
        self.deps.append({"type": d_type, "gov": gov, "dep": dep})
        self.indexed = False

    def remove_tok(self, i):
        self.deps = [
            d for d in self.deps
            if d['gov']['id'] != i and d['dep']['id'] != i]
        self.indexed = False

    def remove_type(self, d_type):
        self.deps = [d for d in self.deps if d['type'] != d_type]
        self.indexed = False

class DependencyProcessor():
    copulars = set([
        "'s", 'are', 'be', 'been', 'being', 'is', 's', 'was', 'were'])

    def __init__(self, cfg):
        self.cfg = cfg
        self.lang = self.cfg.get("deps", "lang")

    def process_coordination_stanford(self, deps):
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

    def process_negation(self, deps):
        for dep in deps.get_dep_list():
            dtype, w1, w2 = dep
            if dtype == 'neg' and w2[0] != 'not':
                deps.remove(dep)
                deps.add((dtype, w1, ('not', w2[1])))
        return deps

    def process_copulars(self, deps):
        # nsubj(is, x), prep_P(is, y) -> prep_P(x, y)
        # rcmod(x, is), prep_P(is, y) -> prep_P(x, y)
        copulars = [(word, w_id) for word, w_id in deps.index.iterkeys()
                    if word in DependencyProcessor.copulars]
        new_deps = []
        for cop in copulars:
            if 'nsubj' in deps.index[cop][0]:
                for dep, words in deps.index[cop][0].iteritems():
                    if dep.startswith('prep_'):
                        for word2 in words:
                            new_deps += [
                                (dep, word3, word2)
                                for word3 in deps.index[cop][0]['nsubj']]
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

    def process_conjunction_magyarlanc(self, deps):
        # for all conj(x, conj), for all D(conj, y) create D(x, y)
        # where conj in (hogy, de)
        # get conj dependants of conj relations
        conjs = set((
            d['dep']['id']
            for d in deps.dep_index['conj']
            if d['dep']['lemma'] in ('hogy', 'de')))
        # then for each of these:
        for conj in conjs:
            # get all their governors
            govs = [
                d['gov']
                for d in deps.tok_index[conj][2] if d['type'] == 'conj']
            # then for all dependents of hogy,
            for dep in deps.tok_index[conj][1]:
                # copy each dependency to each governor
                for gov in govs:
                    deps.add(dep['type'], gov, dep['dep'])

            deps.remove_tok(conj)
        deps.index()
        return deps

    def process_copulars_magyarlanc(self, deps):
        # mapping all pairs of the form nsubj(x, c) and pred(c, y)
        # (such that c is a copular verb) to the relation subj(x, y)
        pred_gov_cop_ids = [
            d['gov']['id'] for d in deps.dep_index['pred']
            if d['gov']['lemma'] == 'van']
        for gov_id in pred_gov_cop_ids:
            subj_deps = [d['dep'] for d in deps.tok_index[gov_id][1]]
            for subj in subj_deps:
                preds = [
                    d['dep'] for d in deps.tok_index[gov_id][1]
                    if d['type'] == 'pred']
                for pred in preds:
                    deps.add("subj", subj, pred)
            deps.remove_tok(gov_id)
        deps.index()
        return deps

    def process_coordination_magyarlanc(self, deps):
        # get governors of coord relations
        govs = set((d['gov']['id'] for d in deps.dep_index['coord']))
        # then for each of these:
        for gov in govs:
            # get dep-neighbours of each of these
            coord = [
                d['dep']['id'] for d in deps.tok_index[gov][1]
                if d['type'] in ('coord', 'conj')]
            # print 'coord:', [deps.tok_index[c][0]['lemma'] for c in coord]
            coord += [
                d['gov']['id'] for d in deps.tok_index[gov][2]
                if d['type'] in ('coord', 'conj')]
            # print 'coord:', [deps.tok_index[c][0]['lemma'] for c in coord]
            # and unify their relations
            # logging.info('unifying these:')
            # for c in coord:
            #     logging.info(u"{0}".format(
            #         deps.tok_index[c][0]['word']))
            gov_tok = deps.tok_index['gov'][0]
            if gov_tok is None or gov_tok['msd'][0] != 'C':
                # if the gov is not a conjunction, then it must take part
                # in the unification
                coord.append(gov)
            else:
                # otherwise it should be removed
                deps.remove_tok(gov)

            deps = self.unify_dependencies(
                coord, deps, exclude=set(['coord', 'punct']))

        # we reindex in the end only!
        deps.index()
        return deps

    def unify_dependencies(self, tokens, deps, exclude):
        for tok1 in tokens:
            for tok2 in tokens:
                if tok2 == tok1:
                    continue
                for dep in deps.tok_index[tok1][1]:
                    if dep['type'] in exclude:
                        continue
                    # logging.info('copying: {0}'.format(dep))
                    deps.add(dep['type'], deps.tok_index[tok2][0], dep['dep'])
                for dep in deps.tok_index[tok1][2]:
                    if dep['type'] in exclude:
                        continue
                    # logging.info('copying: {0}'.format(dep))
                    deps.add(dep['type'], dep['gov'], deps.tok_index[tok2][0])
        return deps

    def process_dependencies(self, deps):
        if self.lang == 'en':
            return self.process_stanford_dependencies(deps)
        elif self.lang == 'hu':
            return self.process_magyarlanc_dependencies(deps)
        else:
            raise Exception('unsupported language: {0}'.format(self.lang))

    def process_magyarlanc_dependencies(self, deps):
        deps = NewDependencies(deps)
        deps.remove_type('punct')
        deps.index()
        deps = self.process_conjunction_magyarlanc(deps)
        deps = self.process_copulars_magyarlanc(deps)
        deps = self.process_coordination_magyarlanc(deps)
        return deps.deps

    def process_stanford_dependencies(self, dep_strings):
        try:  # TODO
            deps = Dependencies.create_from_strings(dep_strings)
        except TypeError:
            deps = Dependencies(dep_strings)
        deps = self.process_copulars(deps)
        deps = self.remove_copulars(deps)
        deps = self.process_rcmods(deps)
        deps = self.process_negation(deps)
        # deps = self.process_coordinated_root(deps)
        deps = self.process_coordination_stanford(deps)

        return NewDependencies.create_from_old_deps(deps).deps
