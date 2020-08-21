import datetime
import logging
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from ftis.common.io import write_json, read_json
from ftis.common.exceptions import InvalidSource
from ftis.common.utils import ignored_keys, create_hash


class FTISProcess:
    """Class that represents the life cycle of a 'FTIS' execution"""

    def __init__(self, source, folder, mode="chain"):
        self.folder = Path(folder).expanduser().resolve()
        self.corpus = source
        self.source = source.items  # FIXME this is confusing
        self.chain = []
        self.logger = logging.getLogger(__name__)
        self.console = Console()
        self.mode = mode
        self.metadata = {}
        self.prev_meta = {}

    def setup(self):
        """Makes an initial parse of the yaml file and initialises logging"""
        self.folder.mkdir(exist_ok=True)

        # Create a place to store microcached results
        self.cache = self.folder / ".cache"
        self.cache.mkdir(exist_ok=True)

        # Setup logging and meta path
        self.metapath = self.folder / "metadata.json"
        logfile_path = self.folder / "logfile.log"

        # Read in previous metadata if exists
        try:
            self.prev_meta = read_json(self.metapath)
        except FileNotFoundError:
            self.prev_meta = None

        self.logger.setLevel(logging.DEBUG)

        if logfile_path.exists():
            logfile_path.unlink()

        logfile_handler = logging.FileHandler(logfile_path)
        formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
        logfile_handler.setFormatter(formatter)
        self.logger.addHandler(logfile_handler)
        self.logger.debug("Logging initialised")

    def general_metadata(self):
        # Time
        self.metadata["time"] = datetime.datetime.now().strftime("%H:%M:%S | %B %d, %Y")

        # Analyser chain
        self.metadata["io"] = str([link.name for link in self.chain])

    def fprint(self, text):
        self.console.print(text, style="yellow underline")

    def add(self, *args):
        """Accepts any number of classes to chain together"""
        self.chain = args  # Lets store these classes somewhere

        analyser_params = {}
        for i, analyser in enumerate(self.chain):
            analyser.order = i
            name = analyser.__class__.__name__

            analyser_params[f"{i}_{name}"] = {
                k: v for k, v in vars(analyser).items() if k not in ignored_keys
            }
            analyser.process = self
            analyser.set_dump()

        self.metadata["analyser"] = analyser_params
        # self.order_hash = create_hash(*[x.name for x in self.chain]) #FIXME moot?

    def run_analysers(self):
        for i, analyser in enumerate(self.chain):
            if self.mode == "chain":
                if i == 0:
                    analyser.input = self.source
                else:
                    analyser.input = self.chain[i - 1].output
            else:
                analyser.input = self.source
            analyser.create_identity()
            self.metadata["analyser"][f"{i}_{analyser.name}"]["identity_hash"] = analyser.identity_hash
            analyser.do()

    def run(self):
        self.setup()
        md = "# **** FTIS v0.3 ****"
        md += f"\n\n**Source: {self.corpus.path}**"
        md += f"\n\n**Output: {self.folder}**"
        md += "\n\n---------------------"
        md += "\n\nBeginning processing..."
        self.console.print(Markdown(md))
        print("\n")
        self.run_analysers()
        self.general_metadata()
        write_json(self.metapath, self.metadata)
