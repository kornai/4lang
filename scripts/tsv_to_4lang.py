"""use text_to_4lang to process tsv-formatted dependencies
(instead of parsing ourselves)"""
import json
import logging
import os
import sys

from hunmisc.corpustools.tsv_tools import sentence_iterator, get_dependencies

from fourlang.text_to_4lang import TextTo4lang
from fourlang.utils import get_cfg

def main():
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1]
    cfg = get_cfg(cfg_file)
    text_to_4lang = TextTo4lang(cfg)
    fn = cfg.get('text', 'input_sens')
    base_fn = os.path.basename(fn)
    deps_fn = os.path.join(text_to_4lang.deps_dir, "{0}.deps".format(base_fn))

    if text_to_4lang.lang == 'hu':
        id_field, word_field, lemma_field, msd_field, gov_field, dep_field = (
            0, 1, 3, 4, -4, -2)
    else:
        id_field, word_field, lemma_field, msd_field, gov_field, dep_field = (
            0, 1, None, None, -4, -3)

    deps = map(lambda s: get_dependencies(
        s, id_field, word_field, lemma_field, msd_field, gov_field, dep_field),
        sentence_iterator(open(fn)))

    if text_to_4lang.lang == 'en':
        c_deps = []
        for sen in deps:
            c_deps.append([])
            for d in sen:
                c_deps[-1].append((
                    d['type'],
                    (d['gov']['word'], d['gov']['id']),
                    (d['dep']['word'], d['dep']['id'])))
                # convert to old deps (for now, see issue #51)
    else:
        c_deps = deps
    with open(deps_fn, 'w') as out_f:
        out_f.write("{0}\n".format(json.dumps({
            "deps": c_deps,
            "corefs": []})))

    text_to_4lang.process_deps(deps_fn)

if __name__ == "__main__":
    main()
