import os
import pickle
from typing import List, Dict

import numpy as np
from sklearn import preprocessing

from read_data import Game, ActionInterval, read_file, ActionType, Race, HotkeyAction

onehotkey = preprocessing.OneHotEncoder(categories='auto')
X = [[x] for x in range(11)]
onehotkey.fit(X)


def onehotkey_f(hotkey):
	return onehotkey.transform([[hotkey]]).toarray()[0]


onehotrace = preprocessing.OneHotEncoder(categories='auto')
X = [[x] for x in range(3)]
onehotrace.fit(X)


def onehotrace_f(race):
	return onehotrace.transform([[race]]).toarray()[0]


class Features:
	race: Race
	max_click: int
	avg_click: int
	uses_per_key: Dict[int, int]
	creations_per_key: Dict[int, int]
	updates_per_key: Dict[int, int]
	ratio_use_create_and_update_per_key: Dict[int, int]
	first_used_hotkey: int
	first_created_hotkey: int
	first_updated_hotkey: int
	max_creations_in_row: int
	max_uses_in_row: int
	max_updates_in_row: int
	base_clicks: int
	mineral_clicks: int
	game_length: int
	key_use_in_row: Dict[int, int]
	selection_proportion: int
	selection_rate: int
	selection_max: int

	def to_array(self):
		return np.concatenate(
			[
				onehotrace_f(self.race.value),
				[self.max_click, self.avg_click],
				onehotkey_f(self.first_used_hotkey),
				onehotkey_f(self.first_created_hotkey),
				onehotkey_f(self.first_updated_hotkey),
				[self.uses_per_key[x] for x in range(10)],
				[self.creations_per_key[x] for x in range(10)],
				[self.updates_per_key[x] for x in range(10)],
				[self.ratio_use_create_and_update_per_key[x] for x in range(10)],
				[self.max_creations_in_row, self.max_uses_in_row, self.max_updates_in_row],
				[self.mineral_clicks, self.base_clicks],
				[self.key_use_in_row[x] for x in range(10)],
				[self.selection_proportion, self.selection_rate, self.selection_max]
			]).ravel().tolist()


class ComputeFeatures:

	def __get_action_stats_5_seconds(self, intervals: [ActionInterval]):
		a = [len(actions_list.actions) for actions_list in intervals]
		return max(a), sum(a) / len(intervals)

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

	def __get_ratio_use_create_and_update_per_key(self, feature: Features):
		dict = {}
		for key, value in feature.uses_per_key.items():
			dict[key] = value / (feature.updates_per_key[key] + feature.creations_per_key[key] + 1)
		return dict

	def __get_max_actions_in_row(self, intervals: [ActionInterval], hotkeyaction: HotkeyAction):
		current_n = 0
		max_n = 0
		for interval in intervals:
			for action in interval.actions:
				if action.type == ActionType.Hotkey and action.hotkey.action == hotkeyaction:
					current_n += 1
					max_n = max(current_n, max_n)
				else:
					current_n = 0
		return max_n

	def __get_max_actions_in_row_per_key(self, intervals: [ActionInterval], hotkeyaction: HotkeyAction):
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

	def __get_max_same_key_in_row(self, intervals: [ActionInterval]):
		current_n = 0
		current_key = None
		dict = {}
		for i in range(10):
			dict[i] = 0
		for interval in intervals:
			for action in interval.actions:
				if action.type == ActionType.Hotkey:
					if action.hotkey.key == current_key:
						current_n += 1
						dict[current_key] = max(dict[current_key], current_n)
					else:
						current_n = 1
						current_key = action.hotkey.key
		return dict

	def __get_clicks(self, intervals: [ActionInterval]):
		mineral_n, base_n = 0, 0
		for interval in intervals:
			for action in interval.actions:
				if action.type == ActionType.Mineral:
					mineral_n += 1
				elif action.type == ActionType.Base:
					base_n += 1

		mineral_n = mineral_n * 100 / len(intervals)
		base_n = base_n * 100 / len(intervals)
		return mineral_n, base_n

	def __get_selection_stats(self, intervals: [ActionInterval]):
		selection_count, interval_sel, max_sel = 0, 0, 0
		all_count = 0
		for interval in intervals:
			interval_sel = 0
			for action in interval.actions:
				if action.type == ActionType.Selection:
					selection_count += 1
					interval_sel += 1
				all_count += 1
			max_sel = max(max_sel, interval_sel)

		selection_proportion = selection_count * 100 / (all_count + 1)
		selection_rate = selection_count * 100 / (len(intervals) + 1)
		return selection_proportion, selection_rate, max_sel

	def compute_features(self, game: Game) -> Features:
		f = Features()
		f.race = game.race
		f.max_click, f.avg_click = self.__get_action_stats_5_seconds(game.intervals)
		f.uses_per_key = self.__get_action_per_key(game.intervals, HotkeyAction.used)
		f.creations_per_key = self.__get_action_per_key(game.intervals, HotkeyAction.created)
		f.updates_per_key = self.__get_action_per_key(game.intervals, HotkeyAction.updated)
		f.first_used_hotkey = self.__get_first_hotkey_action(game.intervals, HotkeyAction.used)
		f.first_created_hotkey = self.__get_first_hotkey_action(game.intervals, HotkeyAction.created)
		f.first_updated_hotkey = self.__get_first_hotkey_action(game.intervals, HotkeyAction.updated)
		f.game_length = len(game.intervals),
		f.ratio_use_create_and_update_per_key = self.__get_ratio_use_create_and_update_per_key(f)
		f.max_creations_in_row = self.__get_max_actions_in_row(game.intervals, HotkeyAction.created)
		f.max_uses_in_row = self.__get_max_actions_in_row(game.intervals, HotkeyAction.used)
		f.max_updates_in_row = self.__get_max_actions_in_row(game.intervals, HotkeyAction.updated)
		f.mineral_clicks, f.base_clicks = self.__get_clicks(game.intervals)
		f.key_use_in_row = self.__get_max_same_key_in_row(game.intervals)
		f.selection_proportion, f.selection_rate, f.selection_max = self.__get_selection_stats(game.intervals)
		return f


def get_features(filename: str, max_items: int, label_present=True) -> (List[str], List[List]):
	result_filename = filename + "results.bin"
	if os.path.isfile(result_filename):
		with open(result_filename, "rb") as file:
			data = pickle.load(file)
			return data["labels"], data["features"]

	else:
		c = ComputeFeatures()
		features = []
		labels = []
		for data in read_file(filename, max_items, label_present):
			if label_present:
				labels.append(data.playerId)
			features.append(c.compute_features(data).to_array())

		with open(result_filename, "wb") as file:
			pickle.dump({"labels": labels, "features": features}, file)

		return labels, features


def get_feature_objects(filename: str, max_items: int) -> (Dict[str, Features]):
	result_filename = filename + "results_stats.bin"
	if os.path.isfile(result_filename):
		with open(result_filename, "rb") as file:
			return pickle.load(file)

	else:
		c = ComputeFeatures()
		features = dict()
		for data in read_file(filename, max_items, True):
			if data.playerId not in features:
				features[data.playerId] = []
			features[data.playerId].append(c.compute_features(data))

		with open(result_filename, "wb") as file:
			pickle.dump(features, file)

		return features
