init = '''
from .main import @NAME@ as main

__all__ = ["main"]
'''
main = '''
import os
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import printp
from ftis.common.types import Ftypes


class @NAME@(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.logger.debug("Creating @NAME@ instance")
        self.output_type = Ftypes.json
        self.name = "@NAME@".lower()
        self.validate_parameters()

    def run(self):
        """
        In this method you implement the functionality for the analyser.
        Ideally, place the logic between the two loggers.
        """
        self.logger.info(f"Starting {self.name}")
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
