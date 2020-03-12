
import os
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import printp
from ftis.common.types import Ftypes


class FLUID_TRANSIENTS(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.logger.debug("Creating FLUID_TRANSIENTS instance")
                self.input_type = Ftypes.folder
        self.output_type = Ftypes.json
        self.data_container = multiprocessing.Manager().dict()
        self.output_type = Ftypes.json
        self.name = "FLUID_TRANSIENTS".lower()
        self.validate_parameters()

    def run(self):
        """
        In this method you implement the functionality for the analyser.
        Ideally, place the logic between the two loggers.
        """
        self.logger.info(f"Starting {self.name}")
        self.logger.info(f"Finished {self.name}")
