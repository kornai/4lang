"""use text_to_4lang to process tsv-formatted dependencies
(instead of parsing ourselves)"""
import json
import logging
import os
import sys

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

    deps = [[]]
    for line in open(fn):
        dep_str = line.strip()
        if not dep_str:
            deps.append([])
        else:
            deps[-1].append(dep_str)

    with open(deps_fn, 'w') as out_f:
        out_f.write("{0}\n".format(json.dumps({
            "deps": deps,
            "corefs": []})))

    text_to_4lang.process_deps(deps_fn)

if __name__ == "__main__":
    main()
