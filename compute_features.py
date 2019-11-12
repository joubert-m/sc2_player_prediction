from read_data import Hotkey, Game, ActionInterval, read_file, ActionType

class Features:
	race: str
	min_click_5_s: int
	max_click_5_s: int
	click_frequency: int
	most_used_key: int
	actions_per_key: {}
	first_used_hotkey: Hotkey
	created_hotkeys_start: Hotkey

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
		return max(dict, key=dict.get), dict

	def __get_first_used_hotkey(self, intervals: [ActionInterval]):
		for interval in intervals:
			for action in interval.actions:
				if action.type == ActionType.Hotkey:
					return action.hotkey.key

	def compute_features(self, game: Game):
		f = Features()
		f.race = game.race
		f.min_click_5_s, f.max_click_5_s = self.__get_max_min_click_5_seconds(game.intervals)
		f.click_frequency = self.__get_click_frequency(game.intervals)
		f.most_used_key, f.actions_per_key = self.__get_most_used_key(game.intervals)
		f.first_used_hotkey = self.__get_first_used_hotkey(game.intervals)
		return f

c = ComputeFeatures()
features = []
for data in read_file():
	features.append(c.compute_features(data))

print(features)
