import logging
import sys

from dep_to_4lang import DepTo4lang
from utils import get_cfg


__LOGLEVEL__ = logging.INFO

class Context():
    def __init__(self, cfg):
        self.cfg = cfg
        self.dfl = DepTo4lang(cfg)

    def build_from_deps(self):
        dep_files = self.cfg.get('context', 'dep_files')


def main():
    logging.basicConfig(
        level=__LOGLEVEL__,
        format="%(asctime)s : " +
        "%(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None

    cfg = get_cfg(cfg_file)
    context = Context(cfg)
    context.build_from_deps()
