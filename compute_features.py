import marshal
import os
from typing import List, Dict

import numpy as np
from sklearn import preprocessing

from read_data import Game, ActionInterval, read_file, ActionType, Race, HotkeyAction

"""
ideas:
factor use/create

"""
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
	min_click: int
	max_click: int
	avg_click: int
	uses_per_key: Dict[int, int]
	creations_per_key: Dict[int, int]
	updates_per_key: Dict[int, int]
	first_used_hotkey: int
	first_created_hotkey: int
	first_updated_hotkey: int
	game_length: int

	def to_array(self):
		return np.concatenate(
			[
				onehotrace_f(self.race.value),
				[self.min_click],
				[self.max_click],
				[self.avg_click],
				onehotkey_f(self.first_used_hotkey),
				onehotkey_f(self.first_created_hotkey),
				onehotkey_f(self.first_updated_hotkey),
				[self.uses_per_key[x] for x in range(10)],
				[self.creations_per_key[x] for x in range(10)],
				[self.updates_per_key[x] for x in range(10)],
				[self.game_length]
			]).ravel().tolist()


class ComputeFeatures:

	def __get_click_stats_5_seconds(self, intervals: [ActionInterval]):
		a = [len(actions_list.actions) for actions_list in intervals]
		return min(a), max(a), sum(a) / len(intervals)

	def __get_action_per_key(self, intervals: [ActionInterval], hotkeyaction: HotkeyAction):
		dict = {}
		for i in range(10):
			dict[i] = 0
		for interval in intervals:
			for action in interval.actions:
				if action.type == ActionType.Hotkey and action.hotkey.action == hotkeyaction:
					dict[action.hotkey.key] += 1

		# normalize
		for i in range(10):
			dict[i] /= (len(intervals) + 1)
		return dict

	def __get_first_hotkey_action(self, intervals: [ActionInterval], hotkeyaction: HotkeyAction):
		for interval in intervals:
			for action in interval.actions:
				if action.type == ActionType.Hotkey and action.hotkey.action == hotkeyaction:
					return action.hotkey.key
		return 10

	def compute_features(self, game: Game) -> Features:
		f = Features()
		f.race = game.race
		f.min_click, f.max_click, f.avg_click = self.__get_click_stats_5_seconds(game.intervals)
		f.uses_per_key = self.__get_action_per_key(game.intervals, HotkeyAction.used)
		f.creations_per_key = self.__get_action_per_key(game.intervals, HotkeyAction.created)
		f.updates_per_key = self.__get_action_per_key(game.intervals, HotkeyAction.updated)
		f.first_used_hotkey = self.__get_first_hotkey_action(game.intervals, HotkeyAction.used)
		f.first_created_hotkey = self.__get_first_hotkey_action(game.intervals, HotkeyAction.created)
		f.first_updated_hotkey = self.__get_first_hotkey_action(game.intervals, HotkeyAction.updated)
		f.game_length = len(game.intervals)
		return f


def get_features(filename: str, max_items: int, label_present=True) -> (List[str], List[List]):
	result_filename = filename + "results.bin"
	if os.path.isfile(result_filename):
		with open(result_filename, "rb") as file:
			ms = marshal.load(file)
			return ms["labels"], ms["features"]

	else:
		c = ComputeFeatures()
		features = []
		labels = []
		for data in read_file(filename, max_items, label_present):
			if label_present:
				labels.append(data.playerId)
			features.append(c.compute_features(data).to_array())

		with open(result_filename, "wb") as file:
			marshal.dump({"labels": labels, "features": features}, file)

		return labels, features
