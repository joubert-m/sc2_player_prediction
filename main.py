from typing import List

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from compute_features import get_features

labels: List[str]
features: List[List]
labels, features = get_features("data/TRAIN.CSV")

# Using the train_test_split to create train and test sets.
x_train, x_test, y_train, y_test = train_test_split(features, labels, random_state=22051996, test_size=0.25)

dtc = DecisionTreeClassifier()
dtc.fit(x_train, y_train)

y_pred = dtc.predict(x_test)

print('Accuracy Score on train data: ', accuracy_score(y_true=y_train, y_pred=dtc.predict(x_train)))
print('Accuracy Score on test data: ', accuracy_score(y_true=y_test, y_pred=y_pred))
