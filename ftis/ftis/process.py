import os
import datetime
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
        self.source = ""
        self.base_dir = ""
        self.chain = []

    def validate_config(self):
        """I validate the configuration file"""

        try:
            self.config.keys()
        except AttributeError:
            raise InvalidYamlError(
                "No sections configuring analysis and processing stages"
            )
        try:
            self.config.values()
        except AttributeError:
            raise InvalidYamlError(
                "No configuration for the analysis and processing sections"
            )

        keys = self.config.keys()
        if "source" not in keys:
            raise InvalidYamlError("No source is specified")
        if "analysers" not in keys:
            raise InvalidYamlError("No analysers are specified")
        if "folder" not in keys:
            raise InvalidYamlError("No output folder specified")

        for analyser in self.config["analysers"]:
            # Test that all of the analysers can be imported without error
            try:
                import_analyser(analyser)
            except ImportError:
                raise AnalyserNotFound(f"{analyser} is not a valid analyser")

    def parse_config(self):
        self.base_dir = expand_tilde(self.config["folder"])
        self.source = expand_tilde(self.config["source"])

    def build_processing_chain(self):
        """
        Builds the processing chain in the right order
        """
        for index, analyser in enumerate(self.config["analysers"]):

            Analyser = import_analyser(analyser)
            analyser = Analyser(self.config)
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
        ...that the chain can be guaranteed to have matching io
        """
        raise NotYetImplemented

    def create_metadata(self):
        # Date/time/input/file list/
        # List chain
        time = datetime.datetime.now().strftime("%H:%M:%S | %B %d, %Y")
        metadata = {"time": time}
        io =[]
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
        self.validate_config()
        self.parse_config()
        self.build_processing_chain()
        # THIS IS WHERE YOU WOULD VALIDATE INPUTS AND OUTPUTS

        # Assume here that all of the necessary checks have passed successfully
        # So we make sure that the output folder exists
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.create_metadata()
        self.run_analysers()
