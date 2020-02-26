import os, sys, time, tempfile, argparse, subprocess
import multiprocessing as mp
from shutil import copyfile, rmtree
from ftis.utils import bufspill, write_json, printp

parser = argparse.ArgumentParser(description='Slice a folder of audio files using fluid-noveltyslice.')
parser.add_argument('-i', '--infolder', required=True, type=str,               help='The input folder to analyse')
parser.add_argument('-o', '--outfile',  requried=True, type=str,               help='The output JSON containing analysis')
parser.add_argument('-f', '--fftsettings', type=str, default="4096 1024 4096", help='The fftsettings')
parser.add_argument('-b', '--numbands',    type=str, default="13",             help='Number of bands to compute MFCC with')
parser.add_argument('-c', '--numcoeffs',   type=str, default="13",             help='Number of coefficients to produce from MFCC')
parser.add_argument('-d', '--numderivs',   type=str, default="3",              help='Number of derivatives to compute stats with')

args = parser.parse_args()

# You need to pass in the input directory and the output file
if not args.infolder or not args.outfile:
    print('You need to provide an input folder/output file.')
    exit()

this_script = os.path.dirname(os.path.realpath(__file__))

# Prepare for work
tmp_dir = tempfile.mkdtemp()
input_folder = args.infolder
input_files = os.listdir(input_folder)
output_json = args.outfile

# dict with shared memory between processes for writing out results
mfcc_dict = mp.Manager().dict()

fftsettings = args.fftsettings.split(" ")
def analyse(idx: int):
    # Setup paths/files etc
    mfcc_src        = os.path.join(input_folder, input_files[idx])
    mfcc_features   = os.path.join(tmp_dir, f'{input_files[idx]}_features.wav')
    mfcc_stats      = os.path.join(tmp_dir, f'{input_files[idx]}_stats.wav' )
    # Compute spectral shape descriptors
    subprocess.call([
        'fluid-mfcc', 
        '-source', mfcc_src, 
        '-features', mfcc_features, 
        '-fftsettings', fftsettings[0], fftsettings[1], fftsettings[2],
        '-numbands', args.numbands,
        '-numcoeffs', args.numcoeffs,
        '-maxnumcoeffs', args.numcoeffs
    ])
    # Now get the stats of the shape analysis
    subprocess.call([
        'fluid-stats', 
        '-source', mfcc_features, 
        '-stats', mfcc_stats,
        '-numderivs', args.numderivs
    ])
    data = bufspill(mfcc_stats)
    try:
        data = data.flatten()
        list_data = data.tolist()
        mfcc_dict[input_files[idx]] = list_data
    except:
        print(f'There was no data to process for {mfcc_src}.')

num_jobs = len(input_files)

# Insert metadata at the top
mfcc_dict["meta"] = {
    "fftsettings" : args.fftsettings,
    "numbands" : args.numbands,
    "numcoeffs" : args.numcoeffs,
    "numbands" : args.numbands,
    "numderivs" : args.numderivs,
    "numjobs" : num_jobs
}

with mp.Pool() as pool:
    for i, _ in enumerate(
        pool.imap_unordered(analyse, range(num_jobs)), 1):
            sys.stderr.write('\rAnalysis Progress {0:%}'.format(i/num_jobs))

write_json(output_json, dict(mfcc_dict))
rmtree(tmp_dir)
printp('Finished analysis')