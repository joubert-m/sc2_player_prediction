import csv
import sys
from typing import List
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, GridSearchCV

from compute_features import get_features

MAX_ITEMS = sys.maxsize
RANDOM_STATE = 80085
TRAIN_DATA_PATH = "data/TRAIN.CSV"
TEST_DATA_PATH = "data/TEST.CSV"
SUBMIT_FILE = "data/submission.CSV"

labels: List[str]
features: List[List]
labels, features = get_features(TRAIN_DATA_PATH, MAX_ITEMS)

# Using the train_test_split to create train and test sets.
x_train, x_test, y_train, y_test = train_test_split(features, labels, random_state=RANDOM_STATE, test_size=0.2)

parameters_dict = {
	"n_estimators": [256],
	"max_features": [x/100 for x in range(10, 60, 5)],
	"max_depth": [x for x in range(1, 21, 1)],
	"min_samples_split": [x for x in range(2, 8, 2)],
	"min_samples_leaf": [x for x in range(1, 5, 1)],
	"criterion": ["gini"],
	"random_state": [RANDOM_STATE]
}

estimator = RandomForestClassifier()
search = GridSearchCV(estimator=estimator, param_grid=parameters_dict, n_jobs=-1, verbose=10, cv=5)
search.fit(x_train, y_train)

print(search.best_score_)
print(search.best_params_)

print('Accuracy Score on train data: ', accuracy_score(y_true=y_train, y_pred=search.predict(x_train)))
print('Accuracy Score on test data: ', accuracy_score(y_true=y_test, y_pred=search.predict(x_test)))

"""
TEST FOR SUBMISSIONS
"""
feature_importances = list(map(lambda x: round(x, 4) * 100, search.best_estimator_.feature_importances_))
labeled_features, count = [], 0
agg, start = [3, 1, 1, 10, 10, 10, 10, 10, 10, 10], 0
for i in agg:
	for j in range(start, start+i):
		count += feature_importances[j]
	start += i
	labeled_features.append(count)
	count = 0

print("------- Feature importances ------")
print(labeled_features)


input("Do you want to predict test with this model ? The current submission.csv will be deleted ... press enter")
print("predict and write...")
labels_test_null, x_test = get_features(TEST_DATA_PATH, MAX_ITEMS, label_present=False)
test_predicted_labels = search.predict(x_test)
with open(SUBMIT_FILE, mode='w', newline='') as file:
	submission = csv.writer(file, delimiter=',', quotechar='"')
	submission.writerow(['RowId', 'prediction'])
	for i, label in enumerate(test_predicted_labels):
		submission.writerow([str(i + 1), label])