from ftis.common.analyser import FTISAnalyser


class MFCC(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.name = "mfcc"
        self.parameters = {
            "fftsettings": "4096 1024 4096",
            "numbands": 40,
            "numcoeffs": 13
        }
        self.validate_parameters()

    def run(self, input, output):
        