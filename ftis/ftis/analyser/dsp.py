# class FluidSines(FTISAnalyser):
#     def __init__(self,
#     bandwidth=76,
#     birthhighthreshold=-60,
#     birthlowthreshold=-24,
#     detectionthreshold=-96,
#     fftsettings=[1024, 512, 1024],
#     mintracklen=15,
#     trackingmethod=0,
#     trackfreqrange=50.0,
#     trackmagrange=15.0,
#     trackprob=0.5
#     ):
#         super().__init__()
#         self.bandwidth = bandwidth,
#         self.birthhighthreshold,
#         self.birthlowthreshold,
#         self.detectionthreshold,
#         self.fftsettings,
#         self.mintracklen

#     def analyse(self, workable):
#         out_folder = self.output / workable.name
#         out_folder.mkdir(exist_ok=True)

#         sines = out_folder / f"sines_{workable.name}"
#         residual = out_folder / f"residual_{workable.name}"

#         fluid.sines(
#             workable,
#             sines=sines,
#             residual=residual,
#             bandwidth=self.parameters["bandwidth"],
#             birthhighthreshold=self.parameters["birthhighthreshold"],
#             birthlowthreshold=self.parameters["birthlowthreshold"],
#             detectionthreshold=self.parameters["detectionthreshold"],
#             fftsettings=self.parameters["fftsettings"],
#             mintracklen=self.parameters["mintracklen"],
#             trackingmethod=self.parameters["trackmethod"],
#             trackfreqrange=self.parameters["trackfreqrange"],
#             trackmagrange=self.parameters["trackmagrange"],
#             trackprob=self.parameters["trackprob"],
#         )

#     def run(self):
#         workables = self.input
#         singleproc(self.name, self.analyse, workables)
#         self.output

# class FluidTransients(FTISAnalyser):
#     def __init__(self):
#         super().__init__(parent_process)
#         self.input_type = Ftypes.folder
#         self.output_type = Ftypes.folder

#     def analyse(self, workable):
#         out_folder = self.output / workable.name
#         out_folder.mkdir(exist_ok=True)

#         transients = out_folder / f"transients_{workable.name}"
#         residual = out_folder / f"residual_{workable.name}"

#         fluid.transients(
#             workable,
#             transients=transients,
#             residual=residual,
#             blocksize=self.parameters["blocksize"],
#             clumplength=self.parameters["clumplength"],
#             order=self.parameters["order"],
#             padsize=self.parameters["padsize"],
#             skew=self.parameters["skew"],
#             threshback=self.parameters["threshback"],
#             threshfwd=self.parameters["threshfwd"],
#             windowsize=self.parameters["windowsize"],
#         )

#     def run(self):
#         workables = self.input
#         multiproc(self.name, self.analyse, workables)
#         cleanup()
