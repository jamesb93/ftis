import datetime
import logging
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from ftis.common.io import write_json, read_json
from ftis.common.exceptions import InvalidSource
from ftis.common.utils import ignored_keys, create_hash
from ftis.corpus import Corpus
from shutil import rmtree

class World:
    def __init__(self, source=None, sink=None):
        self.sink = Path(sink).expanduser().resolve()
        self.node_depth = 0

    def process_child_nodes(self, node):
        node.order = self.node_depth
        for n in node.chain:
            n.process = self
            self.node_depth += 1
            self.process_child_nodes(n)
    
    def add(self, node):
        self.sink.mkdir(exist_ok=True, parents=True)
        # multiplex this out for multiple nodes
        self.process_child_nodes(node)
        node.walk_chain()
