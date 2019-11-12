from enum import Enum

'''
FEATURES
- played race
- min apm and max apm in specific range
- avg apm
- most used hotkey
- first hotkey used
- nb created hotkey 5 first seconds
- nb base and mineral selected

'''
class Race(Enum):
	Protoss = 0
	Zerg = 1
	Terran = 2

class HotkeyAction(Enum):
	created = 0
	updated = 1
	used = 2

class Hotkey:
	key: int
	action: HotkeyAction

class Action:
	selection: str
	hotkey: str

class TimedAction:
	start: int
	end: int
	actions: [Action]

class Player:
	race: Race
	timed_actions: [TimedAction]

with open("data/TRAIN.csv", "r") as file:
	# lines_data = [line.split(',') for line in file]

	data = []
	for line in file:
		line_data = line.split(',')
		print(line_data)
		break
