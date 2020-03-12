
import os
import shutil
from ftis.common.analyser import FTISAnalyser
from ftis.common.exceptions import BinError
from ftis.common.utils import printp


class FLUID_LOUDNESS(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.logger.debug("Creating FLUID_LOUDNESS instance")
        self.name = "FLUID_LOUDNESS".lower()
        self.validate_cli()
        self.validate_parameters()

    @staticmethod
    def validate_cli():
        if not shutil.which("fluid-loudness"):
            raise BinError("fluid-loudness executable not found in PATH")

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
