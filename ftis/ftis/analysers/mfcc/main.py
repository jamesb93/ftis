import os
import sys
import subprocess
import tempfile
import multiprocessing
from shutil import rmtree
from ftis.common.analyser import FTISAnalyser
from ftis.common.ftypes import audio_file
from ftis.common.utils import printp, write_json, bufspill


class MFCC(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.name = "mfcc"
        self.fftsettings = []
        self.data_container = multiprocessing.Manager().dict()
        self.TMP = tempfile.mkdtemp()
        self.validate_parameters()

    def set_output(self, base_dir: str):
        self.output = os.path.join(base_dir, f"{self.name}.json")

    def analyse(self, workable: str):
        # Setup paths/files etc
        src = workable
        base_name = os.path.basename(workable)
        features = os.path.join(self.TMP, f"{base_name}_mfcc.wav")
        # Compute MFCC descriptor
        subprocess.call(
            [
                "fluid-mfcc",
                "-source",
                src,
                "-features",
                features,
                "-fftsettings",
                self.fftsettings[0],
                self.fftsettings[1],
                self.fftsettings[2],
                "-numbands",
                str(self.parameters["numbands"]),
                "-numcoeffs",
                str(self.parameters["numcoeffs"]),
                "-maxnumcoeffs",
                str(self.parameters["numcoeffs"]),
            ]
        )

        data = bufspill(features)
        list_data = data.tolist()
        self.data_container[workable] = list_data

    def run(self):
        workables = []
        printp('Getting workables')
        self.fftsettings = self.parameters["fftsettings"].split(" ")
        # Recursively grab all the files from the input string
        for root, _, files in os.walk(self.input):
            for f in files:
                if os.path.splitext(f)[1] in audio_file:
                    workables.append(os.path.join(root, f))

        num_jobs = len(workables)

        printp('Starting multiprocessing')
        with multiprocessing.Pool() as p:
            for i, _ in enumerate(p.imap_unordered(self.analyse, workables), 1):
                sys.stdout.write(f"\rAnalyse Progress {(i/num_jobs) * 100.0}")

        write_json(self.output, dict(self.data_container))
        rmtree(self.TMP)

        printp("Finished MFCC analysis")