import datetime
import logging
import git
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from ftis.common.exceptions import (
    InvalidYamlError,
    AnalyserNotFound,
    ChainIOError,
    SourceIOError,
)
from ftis.common.utils import import_analyser, read_yaml, write_json
from ftis.common.types import Ftypes


class FTISProcess:
    """Class that represents the life cycle of an 'ftis' execution"""

    def __init__(self, source: Path, folder: Path):
        self.folder = Path(folder)
        self.source = Path(source)
        self.chain = []
        self.logger = None
        self.console = Console()
        self.mode = "chain"
        self.setup()

    def setup(self):
        """Makes an initial parse of the yaml file and initialises logging"""
        
        assert self.source.exists()
        self.folder.mkdir(exist_ok=True)

        self.metapath = self.folder / "metadata.json"  # set a metadata path

        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        logfile_path = self.folder / "logfile.log"

        if logfile_path.exists():
            logfile_path.unlink()

        logfile_handler = logging.FileHandler(logfile_path)
        formatter = logging.Formatter(
            "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
        )
        logfile_handler.setFormatter(formatter)
        self.logger.addHandler(logfile_handler)
        self.logger.debug("Logging initialised")

    def fprint(self, text):
        self.console.print(text, style="yellow underline")

    def dry_print(self, text):
        self.console.print(text, style="red underline")

    def add(self, *args):
        """Accepts any number of classes to chain together"""
        self.chain = args  # Lets store these classes somewhere

        for i, analyser in enumerate(self.chain):
            analyser.process = self
            analyser.order = i
            analyser.logger = self.logger
            analyser.set_dump()

    def run_analysers(self):
        for i, obj in enumerate(self.chain):
            if self.mode == "chain":
                if i == 0:
                    obj.input = self.source
                else:
                    obj.input = self.chain[i - 1].output

                if i == len(self.chain) - 1:
                    obj.dumpout = True

            if self.mode == "batch":
                obj.input = self.source
                obj.dumpout = True
            obj.do()

    def create_metadata(self):
        # Time
        time = datetime.datetime.now().strftime("%H:%M:%S | %B %d, %Y")
        metadata = {"time": time}

        # Git Hash
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        metadata["commit_hash"] = sha

        # Analyser chain
        io = [link.name for link in self.chain]
        io.insert(0, str(self.source))
        metadata["io"] = str(io)

        # Analyer Parameters
        # Instead of just copying the config, we're going to look at what parameters were actually set in each analyser
        # This takes into account parameters being assigned in the case that no parameters were set in the config
        # metadata_params = {}
        # for analyser in self.chain:
        #     metadata_params[analyser.__class__.__name__] = analyser.parameters
        # metadata["analysers"] = metadata_params

        write_json(self.metapath, metadata)

    def run(self):
        # self.initial_parse()
        # Pretty table print out here
        md = "# **** FTIS v0.1 ****"
        md += f"\n\n**Source: {self.source}**"
        md += f"\n\n**Output: {self.folder}**"
        md += "\n\n---------------------"
        md += "\n\nBeginning processing..."
        self.console.print(Markdown(md))
        print("\n")
        self.run_analysers()
        self.create_metadata()
