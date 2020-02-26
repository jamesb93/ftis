from ftis.common.exceptions import AnalyserParameterInvalid

class FTISAnalyser():
    """
    Every analyser inherits from this class
    """
    def __init__(self, config):
        self.analyser_config = config
        self.parameters = {} # A place to store the parameters associated to this analyser
        self.input_type = ""
        self.output_type = ""
        self.name = ""
        
    def validate_parameters(self):
        print('Validating parameters')
        for key in self.analyser_config.keys():
            if key not in self.parameters.keys():
                raise AnalyserParameterInvalid(f"'{key}' is not a parameter for {self.name}. Please review your YAML configuration")
    
    def assign_parameters(self):
        print('Assigning Parameters')
    
    @classmethod
    def run(cls, input, output):
        """
        Method for running the processing chain from input to output.
        """
        
