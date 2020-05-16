
import os
from ftis.common.analyser import FTISAnalyser
from ftis.common.types import Ftypes


class CLASSIFICATION(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.logger.debug("Creating CLASSIFICATION instance")
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.json
        self.name = "CLASSIFICATION".lower()
        self.validate_parameters()

    def run(self):
        """
        In this method you implement the functionality for the analyser.
        """
