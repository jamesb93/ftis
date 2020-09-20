# https://i-systems.github.io/teaching/ML/iNotes/15_Autoencoder.html#3.-Autoencoder-with-Scikit-Learn

from sklearn.neural_network import MLPRegressor
from sklearn.datasets import make_regression
import numpy as np


a, b = make_regression(n_samples=10, n_features=5 ,random_state=1)


r = MLPRegressor(
    hidden_layer_sizes=(
        3, 3
    )
    ).fit(a, a)

print(r.coefs_[1])