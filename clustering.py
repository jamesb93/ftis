# https://scikit-learn.org/stable/auto_examples/cluster/plot_dbscan.html#sphx-glr-auto-examples-cluster-plot-dbscan-py
import sys, os, hdbscan, random, argparse
import numpy as np
from shutil import copyfile
from sklearn.cluster import DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from ftis.utils import read_json, write_json, read_yaml, printp, check_make

parser = argparse.ArgumentParser(description='Cluster data')
parser.add_argument('-i', '--infile',  required=True, type=str,            help='The input JSON containing analysis data to reduce')
parser.add_argument('-o', '--outfile', required=True, type=str,            help='The output JSON containing analysis')
parser.add_argument('-a', '--algorithm',    type=str,   default='HDBSCAN', help='The clustering args.algorithm to use')
parser.add_argument('-nc', '--numclusters', type=int,   default=10,        help='The number of clusters to group when using the AP args.algorithm')
parser.add_argument('-e', '--dbseps',       type=float, default=0.01,      help='Epsilon value for DBSCAN parameters')
parser.add_argument('-ms', '--dbminsamps',  type=int,   default=4,         help='Minimum samples for DBSCAN')
args = parser.parse_args()

printp('Reading in data')
unreduced_data = read_json(args.infile)

try:
    del unreduced_data["meta"]
except KeyError:
    print('No metadata key to remove the input dataset.')

keys    = [x for x in unreduced_data.keys()]
values  = [y for y in unreduced_data.values()]

data = np.array(values)

printp('Clustering')
if args.algorithm == 'AP':
    db = AgglomerativeClustering(
        n_clusters=args.numclusters).fit(data)
if args.algorithm == 'DBSCAN':
    db = DBSCAN(
        eps=args.dbseps, 
        min_samples=args.dbsminsamps, n_jobs=-1).fit(data)
if args.algorithm == 'HDBSCAN':
    db = hdbscan.HDBSCAN().fit(data)

cluster_dict: dict = {}

cluster_dict["meta"] = {"algorithm" : args.algorithm}

for audio, cluster in zip(keys, db.labels_):
    if str(cluster) in cluster_dict:
        cluster_dict[str(cluster)].append(audio)
    else:
        cluster_dict[str(cluster)] = [audio]

printp('Writing Out')
write_json(args.outfile, cluster_dict)