from ftis.common.exceptions import InvalidYamlError, AnalyserNotFound
from ftis.common.utils import import_analyser
from importlib import import_module
import os

class FTISProcess():
    """
    I am a class that represents the life cycle of an 'ftis' execution.
    I contain all of the necessary information and classes as well as validating their inputs, outputs and parameters.
    """
    
    def __init__(self):
        self.base_dir = ""
        self.config = {}
        self.chain = []

    def validate_config(self):
        """
        I validate the configuration file
        """
        try:
            keys = self.config.keys()
        except AttributeError:
            raise InvalidYamlError("There are no sections configuring analysis and processing stages. Your config file may be empty or incorrectly structured.")
        try:
            values = self.config.values()
        except AttributeError:
            raise InvalidYamlError("There is no configuration for the analysis and processing sections. Your config file may be empty or incorrectly structured.")

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
            except:
                raise AnalyserNotFound(f"{analyser} is not a valid analyser")

    def process_config(self):
        """
        I process the configuration file into usuable bits.
        I will create instances of every class required and store and pass each class the right parameters/inputs/outputs
        I then call run() for each class in order
        """
        for index, analyser in enumerate(self.config["analysers"]):
            parameters = self.config["analysers"][analyser]

            Analyser = import_analyser(analyser)
            analyser = Analyser(parameters)
            self.chain.append(analyser)
    
    def create_metadata(self):
        # Date/time/input/file list/ list of all the processes and in what order
        pass
                


    def run_analysers(self):
        print('')
        
        
    def run_process(self):
        self.validate_config()
        self.process_config()
        # Assume here that all of the necessary checks have passed successfully
        # So we make sure that the output folder exists
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.run_analysers()

