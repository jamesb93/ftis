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
    """
    Class that represents the life cycle of an 'ftis' execution.
    """

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = read_yaml(self.config_path)
        self.base_dir = ""
        self.source = ""
        self.chain = []
        self.logger = None
        self.console = Console()
        self.mode = ""

    def initial_parse(self):
        """Makes an initial parse of the yaml file and initialises logging"""
        try:
            self.base_dir = Path(self.config["folder"]).expanduser()
        except KeyError:
            raise InvalidYamlError("Config does not contain output folder")

        self.metapath = self.base_dir / "metadata.json" # set a metadata path

        try:
            self.source = Path(self.config["source"]).expanduser()
        except KeyError:
            raise InvalidYamlError("Config does not contain source folder")

        if not self.base_dir.exists():
            self.base_dir.mkdir()

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        logfile_path = self.base_dir / "logfile.log"

        if logfile_path.exists():
            logfile_path.unlink()

        logfile_handler = logging.FileHandler(logfile_path)
        formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
        logfile_handler.setFormatter(formatter)
        self.logger.addHandler(logfile_handler)
        self.logger.debug("Logging initialised")

    def fprint(self, text):
        self.console.print(text, style="yellow underline")

    def dry_print(self, text):
        self.console.print(text, style="red underline")

    def validate_config(self):
        """I validate the configuration file"""
        self.logger.debug("Validating Configuration")
        try:
            keys = self.config.keys()
        except AttributeError as e:
            self.logger.exception(e)
            raise InvalidYamlError("No analysis sections in configs")
        try:
            self.config.values()
        except AttributeError as e:
            self.logger.exception(e)
            raise InvalidYamlError("No analysis sections in config")

        if "source" not in keys:
            self.logger.debug("No source specified in configuration file")
            raise InvalidYamlError("No source is specified")
        if "analysers" not in keys:
            self.logger.debug("No analyers specified in configuration file")
            raise InvalidYamlError("No analysers are specified")
        if "folder" not in keys:
            self.logger.debug("No output folder specified in configuration")
            raise InvalidYamlError("No output folder specified")

        for analyser in self.config["analysers"]: #TODO remove as it can be caught in testing
            # Test that all of the analysers can be imported without error
            try:
                import_analyser(analyser)
            except ImportError as e:
                self.logger.exception(e)
                raise AnalyserNotFound(f"{analyser} is not a valid analyser")

    def build_processing_chain(self):
        """Builds the processing chain in the right order"""

        for index, analyser in enumerate(self.config["analysers"]):
            Analyser = import_analyser(analyser)
            analyser = Analyser(self)
            self.chain.append(analyser)

        for ext in vars(Ftypes).values():
            if ext == self.source.suffix:
                self.source_type = ext
        if self.chain[0].input_type != self.source_type:
            raise SourceIOError()

        try:
            self.mode = self.config["mode"]
        except KeyError:
            self.mode = "chain"

        for index, analyser in enumerate(self.chain):
            analyser.order = index
            analyser.validate_parameters()
            if self.mode == "chain":
                if index == 0:
                    analyser.input = self.source
                else:
                    if analyser.input_type != self.chain[index - 1].output_type:
                        self.logger.debug("Error building chain")
                        raise ChainIOError(analyser, self.chain[index - 1])
                    analyser.input = self.chain[index - 1].output

            if self.mode == "batch":
                if analyser.input_type == self.source_type:
                    analyser.input = self.source
                else:
                    raise ChainIOError(analyser, self.source)

    def create_metadata(self):
        # Time
        time = datetime.datetime.now().strftime("%H:%M:%S | %B %d, %Y")
        metadata = {"time": time}

        # Git Hash
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        metadata["commit_hash"] = sha

        # Analyser chain
        io = [str(link.output) for link in self.chain]
        io.insert(0, str(self.source))
        metadata["io"] = str(io)

        # Analyer Parameters
        # Instead of just copying the config, we're going to look at what parameters were actually set in each analyser
        # This takes into account parameters being assigned in the case that no parameters were set in the config
        metadata_params = {}
        for analyser in self.chain:
            metadata_params[analyser.__class__.__name__] = analyser.parameters
        metadata["analysers"] = metadata_params

        write_json(self.metapath, metadata)

    def run_analysers(self):
        for obj in self.chain:
            obj.do()

    def dry_run_analysers(self):
        for obj in self.chain:
            obj.dry()

    def run_process(self):
        self.initial_parse()
        self.validate_config()
        self.build_processing_chain()
        # Pretty table print out here
        md = "# **** FTIS v0.1 ****"
        for key in self.config:
            if key == "source":
                md += f"\n\n**Source: {self.config[key]}**"
            if key == "folder":
                md += f"\n\n**Output: {self.config[key]}**"
            # if key == "analysers":
            #     md += f"\n\n**Chain:**"
            #     for i, v in enumerate(self.config[key]):
            #         md += f"\n\n{i+1} - {v}"
            #         for x in self.config[key][v]:
            #             md += f"\n\n    {x}: {self.config[key][v][x]}"
        md += "\n\n---------------------"
        md += "\n\nBeginning processing..."
        self.console.print(Markdown(md))
        print("\n")
        self.run_analysers()
        self.create_metadata()

    def dry(self):
        self.initial_parse()
        self.validate_config()
        self.build_processing_chain()
        self.dry_run_analysers()
        self.create_metadata()
