import os
import datetime
import logging
import git
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from ftis.common.exceptions import (
    InvalidYamlError,
    AnalyserNotFound,
    NotYetImplemented,
    ChainIOError,
    SourceIOError
)

from ftis.common.utils import (
    import_analyser,
    read_yaml,
    expand_tilde,
    write_json
)
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
            self.base_dir = expand_tilde(self.config["folder"])
        except KeyError:
            raise InvalidYamlError("Config does not contain output folder")
        try:
            self.source = expand_tilde(self.config["source"])
        except KeyError:
            raise InvalidYamlError("Config does not contain source folder")

        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        logfile_path = os.path.join(self.base_dir, "logfile.log")
        if os.path.isfile(logfile_path):
            os.remove(logfile_path)

        logfile_handler = logging.FileHandler(
            os.path.join(self.base_dir, "logfile.log")
        )
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
        logfile_handler.setFormatter(formatter)
        self.logger.addHandler(logfile_handler)
        self.logger.info("Logging initialised")
    
    def fprint(self, text):
        self.console.print(text, style="magenta underline")

    def validate_config(self):
        """I validate the configuration file"""
        self.logger.info("Validating Configuration")
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

        for analyser in self.config["analysers"]:
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

        if self.config["mode"]:
            self.mode = self.config["mode"]
        else:
            self.mode = "chain"

        if self.mode == "chain":
            for index, analyser in enumerate(self.chain):
                if index == 0:
                    # case the source argument and figure out of its compatible
                    source_ext = os.path.splitext(self.source)[1]
                    for type_string, ext in Ftypes.items():
                        if ext == source_ext:
                            self.source_type = ext
                    
                    if analyser.input_type != self.source_type:
                        raise SourceIOError()
                        
                    analyser.input = self.source
                else:
                    if analyser.input_type != self.chain[index - 1].output_type:
                        self.logger.debug("Error building chain")
                        raise ChainIOError(analyser, self.chain[index-1])
                    analyser.input = self.chain[index - 1].output
        
        # if self.mode == "batch":
        #     for index, analyser in enumerate(self.chain):
        #         if index == 0:
        #             source_ext = os.path.splitext(self.source)[1]
        #             for type_string, ext in Ftypes.items():
        #                 if ext == source_ext:
        #                     self.source_type = ext
        #             if analyser.input_type != self.source:
        #                 raise SourceIOError()

        #         analyser.input = self.source
                        
                    




    def validate_io(self):
        """
        This will be run directly after build_processing_chain
        It will require specific typs to be implemented so...
        ...that the chain can be guaranteed to have compatible io
        """
        raise NotYetImplemented

    def create_metadata(self):
        # file list/
        # Time
        time = datetime.datetime.now().strftime("%H:%M:%S | %B %d, %Y")
        metadata = {"time": time}
        # Git Hash
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        metadata["commit_hash"] = sha

        # Analyser chain
        io = [link.output for link in self.chain]
        io.insert(0, self.source)
        metadata["io"] = io
        write_json(os.path.join(self.base_dir, "metadata.json"), metadata)

    def run_analysers(self):
        for obj in self.chain:
            obj.do()

    def run_process(self):
        self.initial_parse()
        self.validate_config()
        self.build_processing_chain()
        self.create_metadata()
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
        self.console.print(
            Markdown(md)
        )
        print("\n")
        self.run_analysers()