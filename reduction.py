import sys, os, umap, json, argparse
import numpy as np
from shutil import copyfile
from ftis.utils import read_json, write_json, printp, read_yaml, get_path, check_make
from sklearn import decomposition
from sklearn import manifold
from sklearn.preprocessing import MinMaxScaler, StandardScaler

parser = argparse.ArgumentParser(description='Reduce the dimensionality of analysis data')
parser.add_argument('-i', '--infile',     type=str,                          help='The input JSON containing analysis data to reduce')
parser.add_argument('-o', '--outfile',    type=str,                          help='The output JSON containing analysis')
parser.add_argument('-c', '--components', type=int,   default=2,             help='Number of components to reduce data to')
parser.add_argument('-s', '--scaling',    type=str,   default="standardise", help='Method of data scaling before reduction.')
parser.add_argument('-md', '--mindist',   type=float, default=0.1,           help='Minimum distance parameter for UMAP')
parser.add_argument('-n', '--neighbours', type=int,   default=7,             help='Neighbourhood parameter for UMAP')
args = parser.parse_args()

analysis_data = read_json(args.infile)

# scrub that metadata boy!
try: 
    del analysis_data["meta"]
except: 
    print("No Metadata or failed deletion")

data = [v for v in analysis_data.values()]
keys = [k for k in analysis_data.keys()]

if args.scaling == 'minmax':
    printp('Normalising input data')
    scaler = MinMaxScaler()
if  args.scaling == 'standardise':
    printp('Standardising input data')
    scaler = StandardScaler()
# data = np.array(data)
data = scaler.fit_transform(data)

# Fit the transform
printp('Performing UMAP reduction')
reduction = umap.UMAP(
    n_components=args.components, 
    n_neighbors=args.neighbours, 
    min_dist=args.mindist)
printp('Fitting Transform')
data = reduction.fit_transform(data)

# Normalisation
printp('Normalising for JSON output')
post_normalisation = MinMaxScaler()
data = post_normalisation.fit_transform(data)

out_dict = {}

out_dict["meta"] = {
    "components" : args.components,
    "scaling" : args.scaling,
    "mindist" : args.mindist,
    "neighbours" : args.neighbours
}

printp('Outputting JSON')
for key, value in zip(keys, data):  
    out_dict[key] = value.tolist()

write_json(args.outfile, out_dict)