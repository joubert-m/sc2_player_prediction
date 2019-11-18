import marshal
import os
from typing import List, Dict

import numpy as np
from sklearn import preprocessing

from read_data import Game, ActionInterval, read_file, ActionType, Race, HotkeyAction

onehotkey = preprocessing.OneHotEncoder()
X = [[x] for x in range(11)]
onehotkey.fit(X)


def onehotkey_f(hotkey):
	return onehotkey.transform([[hotkey]]).toarray()[0]


onehotrace = preprocessing.OneHotEncoder()
X = [[x] for x in range(3)]
onehotrace.fit(X)


def onehotrace_f(race):
	return onehotrace.transform([[race]]).toarray()[0]


class Features:
	race: Race
	min_click_5_s: int
	max_click_5_s: int
	click_frequency: int
	most_used_key: int
	actions_per_key: Dict[int, int]
	first_used_hotkey: int
	first_created_hotkey: int

	def to_array(self):
		return np.concatenate(
			[onehotrace_f(self.race.value), [self.min_click_5_s], [self.max_click_5_s], [self.click_frequency],
			 onehotkey_f(self.most_used_key), onehotkey_f(self.first_used_hotkey),
			 onehotkey_f(self.first_created_hotkey)]).ravel().tolist()


class ComputeFeatures:

	def __get_max_min_click_5_seconds(self, intervals: [ActionInterval]):
		a = [len(actions_list.actions) for actions_list in intervals]
		return min(a), max(a)

	def __get_click_frequency(self, intervals: [ActionInterval]):
		c, time = 0, int(intervals[-1].start) + 5
		for actions_list in intervals:
			c += len(actions_list.actions)
		return c / time

	def __get_most_used_key(self, intervals: [ActionInterval]):
		dict = {}
		for interval in intervals:
			for action in interval.actions:
				if action.type == ActionType.Hotkey:
					dict[action.hotkey.key] = dict.get(action.hotkey.key, 0) + 1
		return max(dict, key=dict.get) if dict else 10, dict

	def __get_first_used_hotkey(self, intervals: [ActionInterval]):
		for interval in intervals:
			for action in interval.actions:
				if action.type == ActionType.Hotkey and action.hotkey.action == HotkeyAction.used:
					return action.hotkey.key
		return 10

	def __get_first_created_hotkey(self, intervals: [ActionInterval]):
		for interval in intervals:
			for action in interval.actions:
				if action.type == ActionType.Hotkey and action.hotkey.action == HotkeyAction.created:
					return action.hotkey.key
		return 10

	def compute_features(self, game: Game) -> Features:
		f = Features()
		f.race = game.race
		f.min_click_5_s, f.max_click_5_s = self.__get_max_min_click_5_seconds(game.intervals)
		f.click_frequency = self.__get_click_frequency(game.intervals)
		f.most_used_key, f.actions_per_key = self.__get_most_used_key(game.intervals)
		f.first_used_hotkey = self.__get_first_used_hotkey(game.intervals)
		f.first_created_hotkey = self.__get_first_created_hotkey(game.intervals)
		return f


def get_features(filename: str, max_items: int) -> (List[str], List[List]):
	result_filename = filename + "results.bin"
	if os.path.isfile(result_filename):
		with open(result_filename, "rb") as file:
			ms = marshal.load(file)
			return ms["labels"], ms["features"]

	else:
		c = ComputeFeatures()
		features = []
		labels = []
		for data in read_file(filename, max_items):
			labels.append(data.playerId)
			features.append(c.compute_features(data).to_array())

		with open(result_filename, "wb") as file:
			marshal.dump({"labels": labels, "features": features}, file)

		return labels, features
