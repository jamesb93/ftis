
import os
import subprocess
import shlex
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import printp
from ftis.common.types import Ftypes


class SHELL(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.logger.debug("Creating SHELL instance")
        self.input_type = Ftypes["any"]
        self.output_type = Ftypes["any"]
        self.name = "SHELL".lower()
        self.validate_parameters()

    def run(self):
        """
        In this method you implement the functionality for the analyser.
        Ideally, place the logic between the two loggers.
        """
        self.logger.info(f"Starting {self.name}")
        command = shlex.split(
            self.parameters["command"]
        )
        subprocess.call(command)
        self.logger.info(f"Finished {self.name}")
