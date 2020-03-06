import os
from ftis.common.exceptions import AnalyserParameterInvalid, NotYetImplemented
from ftis.common.utils import read_yaml

#TODO: types for input and output
#TODO: required parameters and optional
#TODO: stereo > mono analyser
class FTISAnalyser:
    """Every analyser inherits from this class"""

    def __init__(self, parent_process):
        self.config = parent_process.config
        self.logger = parent_process.logger
        self.input = ""
        self.output = ""
        self.parameters = {}
        self.parameter_template = {}
        self.name = ""
        self.input_type = ""
        self.output_type = ""

    def validate_parameters(self):
        """
        Validates parameters set in the process against the template
        """
        self.logger.info(f"Validating parameters for {self.name}")
        module_parameters = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "analysers",
            self.name,
            "parameters.yaml",
        )
        self.parameter_template = read_yaml(module_parameters)
        self.parameters = self.config["analysers"][self.name]

        # Check that any defined parameters actually exist
        for key in self.parameters:
            if key not in self.parameter_template:
                raise AnalyserParameterInvalid(f"{key} does not exist for {self.name}")

        # If some required keys aren't defined then use defaults
        for key in self.parameter_template:
            if key not in self.parameters:
                self.parameters[key] = self.parameter_template[key]["default"]

        # TODO: Ensure any keys that have options

    def metadata(self):
        """
        TODO: Replace the hardcoded metadata creation
        """

        raise NotYetImplemented

    def set_output(self, base_dir: str):
        """
        Method to create the right output for each analyser
        """

    def validate_io(self):
        """
        I validate whether the input and output types are correct.
        I also create the input and output strings for the class.
        This needs to be implemented in the module definition.
        """

    def run(self):
        """
        Method for running the processing chain from input to output.
        """
