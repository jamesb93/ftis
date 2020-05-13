import os
import sys
import subprocess
import tempfile
import multiprocessing
from shutil import rmtree
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import write_json, bufspill, get_workables
from ftis.common.types import Ftypes
from ftis.common.proc import multiproc



class MFCC(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.logger.debug("Creating MFCC instance")
        self.name = "mfcc"
        self.input_type = Ftypes["folder"]
        self.output_type = Ftypes["json"]
        self.fftsettings = []
        self.data_container = multiprocessing.Manager().dict()
        self.TMP = tempfile.mkdtemp()
        self.validate_parameters()


    def analyse(self, workable: str, task, progress_bar):
        # Setup paths/files etc
        src = workable
        base_name = os.path.basename(workable)
        features = os.path.join(self.TMP, f"{base_name}_mfcc.wav")
        # Compute MFCC descriptor
        subprocess.call([
                "fluid-mfcc",
                "-source", src,
                "-features", features,
                "-fftsettings",
                self.fftsettings[0],
                self.fftsettings[1],
                self.fftsettings[2],
                "-numbands", str(self.parameters["numbands"]),
                "-numcoeffs", str(self.parameters["numcoeffs"]),
                "-maxnumcoeffs", str(self.parameters["numcoeffs"]),
            ])

        progress_bar.update(task, advance = 1)
        data = bufspill(features)[0]
        list_data = data.tolist()
        self.data_container[workable] = list_data

    def run(self):
        
        self.fftsettings = self.parameters["fftsettings"].split(" ")
        workables = get_workables(self.input, ('.wav'))
        multiproc(self.name, self.analyse, workables)

        write_json(self.output, dict(self.data_container))
        rmtree(self.TMP)
