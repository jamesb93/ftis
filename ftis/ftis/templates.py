init = """
from .main import @NAME@ as main

__all__ = ["main"]
"""
main = '''
import os
from ftis.common.analyser import FTISAnalyser
from ftis.common.types import Ftypes


class @NAME@(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.logger.debug("Creating @NAME@ instance")
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.json
        self.name = "@NAME@".lower()
        self.validate_parameters()

    def run(self):
        """
        In this method you implement the functionality for the analyser.
        """
'''

parameters = """
# Parameters are declared first with a node being its name.
# The default for this, and the type are specified in a child node from this.
parameter1:
    default: "4096 1024 4096"

parameter2:
    default: 40

parameter3:
    default: 13.32
"""
