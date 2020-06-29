import os
import subprocess
import shlex
from ftis.common.analyser import FTISAnalyser
from ftis.common.types import Ftypes


class SHELL(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.folder
        self.name = "SHELL".lower()
        self.validate_parameters()

    def run(self):
        """
        In this method you implement the functionality for the analyser.
        Ideally, place the logic between the two loggers.
        """
        command = shlex.split(self.parameters["command"])
        subprocess.call(command)
