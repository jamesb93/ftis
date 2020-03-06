import os
import datetime
import logging
from ftis.common.exceptions import InvalidYamlError, AnalyserNotFound, NotYetImplemented
from ftis.common.utils import import_analyser, read_yaml, expand_tilde, write_json

#TODO: If folder exists prompt the user or make a has or sumting mon

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
        """
        Builds the processing chain in the right order
        """
        for index, analyser in enumerate(self.config["analysers"]):

            Analyser = import_analyser(analyser)
            analyser = Analyser(self)
            self.chain.append(analyser)

        for index, obj in enumerate(self.chain):
            if index == 0:
                obj.input = self.source
            else:
                obj.input = self.chain[index - 1].output
            obj.set_output(self.base_dir)

    def validate_io(self):
        """
        This will be run directly after build_processing_chain
        It will require specific typs to be implemented so...
        ...that the chain can be guaranteed to have compatible io
        """
        raise NotYetImplemented

    def create_metadata(self):
        # Date/time/input/file list/
        # List chain
        time = datetime.datetime.now().strftime("%H:%M:%S | %B %d, %Y")
        metadata = {"time": time}
        io = []
        io.append(self.source)
        for link in self.chain:
            io.append(link.output)
        metadata["io"] = io
        write_json(os.path.join(self.base_dir, "metadata.json"), metadata)

    def run_analysers(self):
        # Something here to do with self.chain
        for obj in self.chain:
            obj.run()

    def run_process(self):
        self.initial_parse()
        self.validate_config()
        self.build_processing_chain()
        # THIS IS WHERE YOU WOULD VALIDATE INPUTS AND OUTPUTS

        # Assume here that all of the necessary checks have passed successfully
        # So we make sure that the output folder exists
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.create_metadata()
        self.run_analysers()
