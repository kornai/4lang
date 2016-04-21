class SimFeatures:
    type_to_fnc = {
        'links_jaccard': 'links_jaccard',
        'subgraphs': 'subgraphs'}

    def links_jaccard(self):
        return {}

    def subgraphs(self):
        return {}

    def __init__(self):
        self.feats_to_get = ['links_jaccard', 'subgraphs']

    def get_feature_class(self, feature_name):
        if feature_name == 'links_jaccard':
            return self.links_jaccard()
        elif feature_name == 'subgraphs':
            return self.subgraphs()

    def get_all_features(self):
        all_feats = {}
        for f in self.feats_to_get:
            all_feats.update(self.get_feature_class(f))
        return all_feats

def test():
    sf = SimFeatures()
    print sf.get_all_features()

if __name__ == "__main__":
    test()
