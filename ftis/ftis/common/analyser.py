import os
from ftis.common.exceptions import NotYetImplemented
from ftis.common.utils import read_yaml
from ftis.common.types import Ftypes


class FTISAnalyser:
    """Every analyser inherits from this class"""
    def __init__(self, parent_process):
        self.parent_process = parent_process
        self.config = self.parent_process.config
        self.logger = self.parent_process.logger
        self.input = ""
        self.output = ""
        self.parameters = {}
        self.parameter_template = {}
        self.name = ""
        self.input_type = ""
        self.output_type = ""

    def validate_parameters(self):
        """
        Validates parameters set in the process against the template.
        This is not an optional function.
        """
        self.logger.debug(f"Validating parameters for {self.name}")
        module_parameters = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "analysers",
            self.name,
            "parameters.yaml",
        )
        self.parameter_template = read_yaml(module_parameters)

        for key in self.parameter_template:
            self.parameters[key] = self.parameter_template[key]["default"]

        if self.config["analysers"]:  # if there is anything at all
            for analyser in self.config["analysers"]:  # assign it
                if self.config["analysers"][analyser]: # in the case that parameters have been assigned
                    for parameter in self.config["analysers"][analyser]:
                        self.parameters[parameter] = self.config["analysers"][analyser][parameter]

        # Calling here stops user having to execute in __init__ class
        self.set_output()

    def metadata(self):
        """
        TODO: Replace the hardcoded metadata creation
        """

        raise NotYetImplemented

    def set_output(self):
        """Create the output for path/type"""
        out = f"{self.name}{self.output_type}"
        self.output = os.path.join(
            self.parent_process.base_dir, 
            out
        )

        if self.output_type == Ftypes["folder"] and not os.path.exists(self.output):
            os.makedirs(self.output)

        self.logger.debug(f"Setting output for {self.name}")

    def validate_io(self):
        """
        I validate whether the input and output types are correct.
        I also create the input and output strings for the class.
        This needs to be implemented in the module definition.
        """
    def do(self):
        self.logger.debug(f"Executing {self.name} run")
        self.run()
        self.logger.debug(f"Finished {self.name} run")
        
    def run(self):
        """
        Method for running the processing chain from input to output.
        """
        
