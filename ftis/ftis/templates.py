init = '''
from .main import @NAME@ as main

__all__ = ["main"]
'''
main = '''
import os
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import printp


class @NAME@(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.logger.debug("Creating @NAME@ instance")
        self.name = "@NAME@"
        self.validate_parameters()

    def set_output(self, base_dir: str):
        """
        In this method you provide the logic for setting the output.
        An example here is given for outputting a json file.
        Any output is valid providing the next link in the chain accepts it.
        """
        self.output = os.path.join(base_dir, f"{self.name}.json")
        self.logger.debug(f"Setting output for {self.name}")

    def run(self):
        """
        In this method you implement the functionality for the analyser
        """
        self.logger.info("Starting {self.name}")
        self.logger.info(f"Finished {self.name}")

'''

parameters = '''
# Parameters are declared first with a node being its name.
# The default for this, and the type are specified in a child node from this.
parameter1:
    default: "4096 1024 4096"
    type: string

parameter2:
    default: 40
    type: int

parameter3:
    default: 13.32
    type: float
'''
