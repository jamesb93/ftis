
import os
import sys
import shutil
import multiprocessing
import tempfile
import subprocess
from shutil import rmtree
from ftis.common.analyser import FTISAnalyser
from ftis.common.exceptions import BinError
from ftis.common.utils import printp, bufspill, write_json
from ftis.common.types import Ftypes


class FLUID_LOUDNESS(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.logger.debug("Creating FLUID_LOUDNESS instance")
        self.name = "FLUID_LOUDNESS".lower()
        self.input_type = Ftypes["folder"]
        self.output_type = Ftypes["json"]
        self.data_container = multiprocessing.Manager().dict()
        self.TMP = tempfile.mkdtemp()
        self.validate_cli()
        self.validate_parameters()

    @staticmethod
    def validate_cli():
        if not shutil.which("fluid-loudness"):
            raise BinError("fluid-loudness executable not found in PATH")

    def analyse(self, workable: str):
        src = workable
        base_name = os.path.basename(workable)
        features = os.path.join(self.TMP, f"{base_name}loudness.wav")
        subprocess.call([
                "fluid-loudness",
                "-maxwindowsize", str(self.parameters["windowsize"]),
                "-windowsize", str(self.parameters["windowsize"]),
                "-hopsize", str(self.parameters["hopsize"]),
                "-kweighting", str(self.parameters["kweighting"]),
                "-truepeak", str(self.parameters["truepeak"]),
                "-source", str(src),
                "-features", str(features)
            ])

        data = bufspill(features)[0]
        list_data = data.tolist()
        self.data_container[workable] = list_data

    def run(self):  
        """
        In this method you implement the functionality for the analyser
        """
        self.logger.info(f"Starting {self.name}")

        workables = []
        printp('Getting workables')
        # Recursively grab all the files from the input string
        for root, _, files in os.walk(self.input):
            for f in files:
                if os.path.splitext(f)[1] in ['.wav']:
                    workables.append(os.path.join(root, f))

        num_jobs = len(workables)

        with multiprocessing.Pool() as p:
            for i, _ in enumerate(p.imap_unordered(self.analyse, workables), 1):
                sys.stdout.write(f"\rAnalyse Progress {(i/num_jobs) * 100.0}")

        write_json(self.output, dict(self.data_container))
        rmtree(self.TMP)

        self.logger.info(f"Finished {self.name}")
