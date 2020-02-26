import os
import sys
import tempfile
import subprocess
import multiprocessing as mp
from ftis.common.analyser import FTISAnalyser
from ftis.common.ftypes import audio_file
from ftis.common.utils import bufspill, write_json, printp
from ftis.common.exceptions import NotYetImplemented
from shutil import rmtree


class MFCC(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.name = "mfcc"
        self.parameters = {
            "fftsettings": "4096 1024 4096",
            "numbands": 40,
            "numcoeffs": 13,
        }
        self.validate_parameters()

    def validate_io(self):
        raise NotImplementedError

    def run(self):
        workables = []
        # Recursively grab all the files from the input string
        for root, _, files in os.walk(self.input):
            for f in files:
                if os.path.splitext(f)[1] in audio_file:
                    workables.append(os.path.join(root, f))
        # Prepare for work
        tmp_dir = tempfile.mkdtemp()
        # dict with shared memory between processes for writing out results
        mfcc_dict = mp.Manager().dict()

        fftsettings = self.parameters["fftsettings"].split(" ")

        def analyse(workable: str):
            # Setup paths/files etc
            mfcc_src = workable
            base_name = os.path.basename(workable)
            mfcc_features = os.path.join(tmp_dir, f"{base_name}_features.wav")
            # Compute MFCC descriptor
            subprocess.call(
                [
                    "fluid-mfcc",
                    "-source",
                    mfcc_src,
                    "-features",
                    mfcc_features,
                    "-fftsettings",
                    fftsettings[0],
                    fftsettings[1],
                    fftsettings[2],
                    "-numbands",
                    str(self.parameters["numbands"]),
                    "-numcoeffs",
                    str(self.parameters["numcoeffs"]),
                    "-maxnumcoeffs",
                    str(self.parameters["numcoeffs"]),
                ]
            )

            data = bufspill(mfcc_features)
            try:
                list_data = data.tolist()
                mfcc_dict[workable] = list_data
            except:
                print(f"There was no data to process for {mfcc_src}.")

        num_jobs = len(workables)

        # Insert metadata at the top
        mfcc_dict["meta"] = {
            "fftsettings": self.parameters["fftsettings"],
            "numbands": self.parameters["numbands"],
            "numcoeffs": self.parameters["numcoeffs"],
            "numjobs": num_jobs,
        }

        for index, workable in enumerate(workables):
            analyse(workable)
            sys.stdout.write(f"\rAnalayse Progress {index/num_jobs}")

        write_json(self.output, dict(mfcc_dict))
        rmtree(tmp_dir)
        printp("Finished MFCC analysis")
