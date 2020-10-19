import datetime
import logging
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from ftis.common.io import write_json, read_json
from ftis.common.utils import ignored_keys, create_hash
from ftis.corpus import Corpus
from shutil import rmtree

class World:
    def __init__(self, source=None, sink=None):
        self.sink = Path(sink).expanduser().resolve()
        self.node_depth = 0
        # Metadata
        self.metadata = {
            "analyser" : []
        }
        self.prev_meta = None
        # Console
        self.console = Console()
        # Logging
        self.logger = logging.getLogger(__name__)

    def build_connections(self, node):
        node.process = self # set the process to the world
        for suborder, child in enumerate(node.chain):
            # Set the parent of the children to the node passed in
            child.parent = node
            # Establish the order
            if isinstance(child.parent, Corpus):
                child.order = 1
            else:
                child.order = child.parent.order + 1
                child.suborder = suborder
            
            # Construct a big metadata file
            # print(
            #     f"Depth: {child.order} | {child.name} | Sub-depth: {suborder} | Parent: {child.parent}"
            # )
            self.build_connections(child)
        # FIXME - parent doesnt show up in the metadata
        self.metadata["analyser"].append({
            k: str(v) 
            for k, v in vars(node).items() 
            if k not in ignored_keys
        })

    def clear_cache(self) -> None:
        rmtree(str(self.cache))

    def setup(self) -> None:
        self.metadata["time"] = datetime.datetime.now().strftime("%H:%M:%S | %B %d, %Y")
        self.sink.mkdir(exist_ok=True, parents=True)
        
        # Microcache
        self.cache = self.sink / ".cache"
        self.cache.mkdir(exist_ok=True)

        # Setup logging and meta path
        self.metapath = self.sink / "metadata.json"
        logfile_path = self.sink / "logfile.log"

        # Load previous meta data if around
        if self.metapath.exists() and self.metapath.is_file():
            self.prev_meta = read_json(self.metapath)

        # Init loggin
        self.logger.setLevel(logging.DEBUG)

        if logfile_path.exists():
            logfile_path.unlink()

        logfile_handler = logging.FileHandler(logfile_path)
        formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
        logfile_handler.setFormatter(formatter)
        self.logger.addHandler(logfile_handler)
        self.logger.debug("Logging initialised")
        
    def build(self, *corpora):
        self.setup()

        # This is a two stage process hence two loops.
        # 1: Build a graph (including depth) of connections
        for c in corpora:
            self.build_connections(c)

        # 2: Walk the chain and run analysers
        for c in corpora:
            c.walk_chain()
            # self.process_child_nodes(c)

        write_json(self.metapath, self.metadata)
        # teardown
        
        
