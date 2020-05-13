import os
import datetime
import logging
import git
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
        self.run_analysers()
