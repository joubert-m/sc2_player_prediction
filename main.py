import sys
from typing import List

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, GridSearchCV

from compute_features import get_features

MAX_ITEMS = sys.maxsize
RANDOM_STATE = 80085
TRAIN_DATA_PATH = "data/TRAIN.CSV"

labels: List[str]
features: List[List]
labels, features = get_features(TRAIN_DATA_PATH, MAX_ITEMS)

# Using the train_test_split to create train and test sets.
x_train, x_test, y_train, y_test = train_test_split(features, labels, random_state=RANDOM_STATE, test_size=0.1)

parameters_dict = {
	"n_estimators": [256],
	"max_depth": np.linspace(10, 100, 4, dtype=int),
	"min_samples_split": np.linspace(2, 50, 8, dtype=int),
	"min_samples_leaf": np.linspace(2, 50, 8, dtype=int),
	"criterion": ["gini"]
}

parameters_dict = {
	"n_estimators": [128],
	"max_features": np.linspace(1, 4, 4, dtype=int),
	"max_depth": np.linspace(10, 100, 10, dtype=int),
	"min_samples_split": [2],
	"min_samples_leaf": [1],
	"criterion": ["gini"]
}

estimator = RandomForestClassifier()
search = GridSearchCV(estimator=estimator, param_grid=parameters_dict, n_jobs=-1, verbose=10, cv=5)
search.fit(x_train, y_train)

print(search.best_score_)
print(search.best_params_)

print('Accuracy Score on train data: ', accuracy_score(y_true=y_train, y_pred=search.predict(x_train)))
print('Accuracy Score on test data: ', accuracy_score(y_true=y_test, y_pred=search.predict(x_test)))
