import os
import sys
import tempfile
import subprocess
import multiprocessing as mp
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import bufspill, write_json, read_json, printp
from ftis.common.exceptions import NotYetImplemented
from shutil import rmtree


class STATS(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.name = "stats"
        self.parameters = {"numderivs": 1}
        self.validate_parameters()
        self.output_type = ".json"
        self.input_type = ".json"

    def validate_io(self):
        raise NotYetImplemented

    def run(self):
        workables = read_json(self.input)
        # Recursively grab all the files from the input string
        # Prepare for work
        tmp_dir = tempfile.mkdtemp()

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
            list_data = data.tolist()
            mfcc_dict[workable] = list_data

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
