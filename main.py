from typing import List

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.tree import DecisionTreeClassifier

from compute_features import get_features

MAX_ITEMS = 100
RANDOM_STATE = 22051996
TRAIN_DATA_PATH = "data/TRAIN.CSV"

labels: List[str]
features: List[List]
labels, features = get_features(TRAIN_DATA_PATH, MAX_ITEMS)

# Using the train_test_split to create train and test sets.
x_train, x_test, y_train, y_test = train_test_split(features, labels, random_state=RANDOM_STATE, test_size=0.25)

parameters_dict = {
	"max_depth": [2, 5, 6, 10],
	"min_samples_split": [0.1, 0.2, 0.3, 0.4],
	"min_samples_leaf": [0.1, 0.2, 0.3, 0.4],
	"criterion": ["gini", "entropy"]
}

dtc = DecisionTreeClassifier(random_state=RANDOM_STATE)
search = RandomizedSearchCV(estimator=dtc)

search.fit(x_train, y_train)

best_dtc = search.best_estimator_

print(search.cv_results_)

print('Accuracy Score on train data: ', accuracy_score(y_true=y_train, y_pred=best_dtc.predict(x_train)))
print('Accuracy Score on test data: ', accuracy_score(y_true=y_test, y_pred=best_dtc.predict(x_test)))
