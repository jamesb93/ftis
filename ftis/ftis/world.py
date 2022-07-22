import datetime
import logging
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich import box
from ftis.common.io import write_json, read_json
from ftis.common.utils import ignored_keys, create_hash
from ftis.corpus import Corpus
from shutil import rmtree

class World:
    def __init__(self, sink=None, quiet=False, clear=False):
        self.sink = Path(sink).expanduser().resolve()
        self.node_depth = 0
        # Input corpora objects
        self.corpora = []
        # Metadata
        self.metadata = {"analyser" : {}}
        self.prev_meta = None
        self.clear = clear
        # Console
        self.console = Console()
        self.quiet = quiet
        # Logging
        self.logger = logging.getLogger(__name__)

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

    def build_connections(self, node):
        node.process = self # set the process to the world
        if not isinstance(node, World):
            node.create_identity()
            node.set_dump()
        for suborder, child in enumerate(node.chain):
            # Set the parent of the children to the node passed in
            child.parent = node
            # Establish the order
            if isinstance(child.parent, Corpus):
                child.order = 1
            else:
                child.order = child.parent.order + 1
                child.suborder = suborder

            self.build_connections(child)
            
        if not isinstance(node, World):
            self.metadata["analyser"][node.identity["hash"]] = {
                k: str(v) 
                for k, v in vars(node).items() 
                if k not in ignored_keys
            }
        
    def build(self, *corpora):
        self.corpora = corpora
        self.setup()
        # This is a two stage process hence two loops.
        # 1: Build a graph (including depth) of connections
        for c in corpora:
            self.build_connections(c)

    def run(self):
        if not self.quiet:
            version = "# **** FTIS ****"
            self.console.print(Markdown(version))
            # Construct information table
            corpora_paths = Table(title="Corpora", box=box.HORIZONTALS, show_lines=True)
            corpora_paths.add_column("Path")
            corpora_paths.add_column("Items", style="cyan")
            for c in self.corpora:
                corpora_paths.add_row(str(c.path), str(len(c.items)))
        
            print("\n")
            self.console.print(corpora_paths)
            sink_text = Text(f" Sink: {self.sink}")
            print("\n")
            self.console.print(sink_text)
            self.console.print(Markdown("---"))
            print("\n")

        for c in self.corpora:
            c.walk_chain()

        self.teardown()

    def teardown(self):
        write_json(self.metapath, self.metadata)
        if self.clear:
            self.clear_cache()

    def fprint(self, text):
        self.console.print(text, style="yellow underline")

    def clear_cache(self) -> None:
        rmtree(str(self.cache))
