import datetime
import logging
import git
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from ftis.common.io import write_json, read_json
from ftis.common.exceptions import InvalidSource


class FTISProcess:
    """Class that represents the life cycle of an 'ftis' execution"""

    def __init__(self, source: Path, folder: Path, mode="chain"):
        self.folder = Path(folder)
        self.source = Path(source)
        self.chain = []
        self.logger = None
        self.console = Console()
        self.mode = mode
        self.metadata = {}
        self.prev_meta = {}
        self.setup()
        self.general_metadata()

    def setup(self):
        """Makes an initial parse of the yaml file and initialises logging"""

        if not self.source.exists():
            raise InvalidSource(self.source)

        self.folder.mkdir(exist_ok=True)

        self.metapath = self.folder / "metadata.json"
        logfile_path = self.folder / "logfile.log"

        # Grab any old metadata
        try:
            self.prev_meta = read_json(self.metapath)
        except FileNotFoundError:
            self.prev_meta = None

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        if logfile_path.exists():
            logfile_path.unlink()

        logfile_handler = logging.FileHandler(logfile_path)
        formatter = logging.Formatter(
            "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
        )
        logfile_handler.setFormatter(formatter)
        self.logger.addHandler(logfile_handler)
        self.logger.debug("Logging initialised")
        
    def general_metadata(self):
        # Time
        time = datetime.datetime.now().strftime("%H:%M:%S | %B %d, %Y")
        self.metadata["time"] = time

        # Git Hash
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        self.metadata["commit_hash"] = sha

        # Analyser chain
        io = [link.name for link in self.chain]
        io.insert(0, str(self.source))
        self.metadata["io"] = str(io)

    def fprint(self, text):
        self.console.print(text, style="yellow underline")

    def add(self, *args):
        """Accepts any number of classes to chain together"""
        self.chain = args  # Lets store these classes somewhere
        # Analyser parameters

        ignored_keys = [ # keys to ignore from superclass
            "process", 
            "logger", 
            "input", 
            "output", 
            "input_type", 
            "dump_type",
            "dumpout",
            "cache",
            "cache_possible"] #FIXME this needs to be not duplicated

        analyser_params = {}
        for i, analyser in enumerate(self.chain):
            analyser.order = i
            name = analyser.__class__.__name__

            params = {}
            for k, v in zip(vars(analyser).keys(), vars(analyser).values()):
                if k not in ignored_keys:
                    params[k] = v
            
            analyser_params[f"{i}_{name}"] = params
            analyser.process = self
            analyser.logger = self.logger
            analyser.set_dump()
        self.metadata["analyser"] = analyser_params

    def run_analysers(self):
        for i, obj in enumerate(self.chain):
            if self.mode == "chain":
                if i == 0:
                    obj.input = self.source
                else:
                    obj.input = self.chain[i - 1].output

                if i == len(self.chain) - 1:
                    obj.dumpout = True

            else:
                obj.input = self.source
                obj.dumpout = True
            obj.do()

    def create_metadata(self):
        # Time
        time = datetime.datetime.now().strftime("%H:%M:%S | %B %d, %Y")
        self.metadata["time"] = time

        # Git Hash
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        self.metadata["commit_hash"] = sha

        # Analyser chain
        io = [link.name for link in self.chain]
        io.insert(0, str(self.source))
        self.metadata["io"] = str(io)

        write_json(self.metapath, self.metadata)

    def run(self):
        md = "# **** FTIS v0.3 ****"
        md += f"\n\n**Source: {self.source}**"
        md += f"\n\n**Output: {self.folder}**"
        md += "\n\n---------------------"
        md += "\n\nBeginning processing..."
        self.console.print(Markdown(md))
        print("\n")

        self.run_analysers()
        self.create_metadata()
