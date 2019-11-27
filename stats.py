import sys
from typing import Dict

from compute_features import get_feature_objects, Features

MAX_ITEMS = sys.maxsize
RANDOM_STATE = 80085
TRAIN_DATA_PATH = "data/TRAIN.CSV"
TEST_DATA_PATH = "data/TEST.CSV"
SUBMIT_FILE = "data/submission.CSV"

features: Dict[str, Features] = get_feature_objects(TRAIN_DATA_PATH, MAX_ITEMS)

print(features.__len__())
