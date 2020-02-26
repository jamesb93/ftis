import sys, os, argparse
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from ftis.utils import read_json, write_json, read_json, cd_up, read_yaml, lines_to_list, printp

parser = argparse.ArgumentParser(description='Crude classification of audio samples with various args.algorithms')
parser.add_argument('-p', '--positive',    required=True, type=str, help='The input JSON containing analysis data to reduce')
parser.add_argument('-n', '--negative',    required=True, type=str, help='The output JSON containing analysis')
parser.add_argument('-d', '--data',        required=True, type=str, help='Path to some analysis data')
parser.add_argument('-o', '--outfile',     required=True, type=str, help='The output JSON containing classification')
parser.add_argument('-f', '--audiofolder', type=str, help='Location of the source audio')
parser.add_argument('-s', '--scaling',     type=str, default="standardise", help='Method of data scaling before reduction.')
parser.add_argument('-a', '--algorithm',   type=str, default='SVM', help='The clustering algorithm to use')
args = parser.parse_args()

printp('Reading in data')
input_data = read_json(args.data)

positive_examples = lines_to_list(args.positive)
negative_examples = lines_to_list(args.negative)

features  = []
label     = []

printp('Creating classification labels')
for example in negative_examples:
    try:
        data = input_data[example]
        features.append(data)
        label.append(0)
    except:
        print(f'Error: Possibly no analysis data for {example}')

for example in positive_examples:
    try:
        data = input_data[example]
        features.append(data)
        label.append(1)
    except:
        print(f'Error: Possibly no analysis data for {example}')

# convert features and labels to numpy arrays
features = np.array(features)
label    = np.array(label)

if args.scaling != 'none':
    if args.scaling == 'minmax':
        scaler = MinMaxScaler()
    if args.scaling == 'standardise':
        scaler = StandardScaler()
    scaler.fit(features)
    features = scaler.transform(features)

# Select Model
if args.algorithm == 'NB':
    ### Naive Bayes ###
    from sklearn.naive_bayes import GaussianNB
    clf = GaussianNB()

if args.algorithm == 'LR':
    ### Logistic Regression ###
    # https://scikit-learn.org/stable/modules/multiclass.html
    from sklearn.linear_model import LogisticRegression
    clf = LogisticRegression()

if args.algorithm == 'SVM':
    ### State Vector Macine ###
    # https://neerajkumar.org/writings/svm/
    from sklearn.svm import SVC
    clf = SVC(gamma='auto')

if args.algorithm == 'linSVC':
    from sklearn.svm import LinearSVC
    clf = LinearSVC(random_state=0, tol=1e-5)

if args.algorithm == 'MLP':
    ## MLP Neural Network ###
    from sklearn.neural_network import MLPClassifier
    clf = MLPClassifier()

if args.algorithm == 'RF':
    from sklearn.ensemble import RandomForestClassifier
    clf = RandomForestClassifier(n_estimators=100,random_state=0, max_depth=1)

printp('Fitting Transform')
# Compute the fit
clf.fit(features, label)

# Classification and JSON formation
classification_dict = {}
good_predictions = []
bad_predictions = []

printp('Classifying new data')
for entry in input_data:
    values = input_data[entry]
    t_data = np.asarray(values)

    if args.scaling != 'none':
        t_data = scaler.transform([t_data])
    else:
        t_data = [t_data]

    prediction = clf.predict(t_data)

    if prediction == 1:
        good_predictions.append(entry)
        # walkman(os.path.join(unique_audio_folder, entry))
    elif prediction == 0:
        bad_predictions.append(entry)

printp('Writing out classification to JSON')
classification_dict['0'] = bad_predictions
classification_dict['1'] = good_predictions

out_file = os.path.join(args.outfile)
write_json(out_file, classification_dict)