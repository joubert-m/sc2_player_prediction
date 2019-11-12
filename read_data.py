from enum import Enum

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

class ActionType:
	Selection = 0
	Base = 1
	Mineral = 2
	Hotkey = 3

class Action:
	type: ActionType
	hotkey: Hotkey

	def __init__(self, type):
		self.type = type

class ActionInterval:
	start: int
	actions: [Action]

	def __init__(self, start):
		self.start = start
		self.actions = []

class Game:
	playerId: str
	race: Race
	intervals: [ActionInterval]

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

def read_file() -> [Game]:
	games: [Game] = []
	# Limit to 10 for testing
	c = 0
	with open("data/TRAIN.CSV", "r") as file:
		# lines_data = [line.split(',') for line in file]
		for line in file:
			line_data = line.split(',')

			g = Game()
			g.playerId = line_data[0]
			g.race = line_data[1]
			g.intervals = []

			interval = ActionInterval(0)
			g.intervals.append(interval)
			for i in range(2, len(line_data)):
				line = line_data[i].rstrip()
				# New interval
				if line[0] == "t":
					interval = ActionInterval(line[1:])
					g.intervals.append(interval)

				# Selection
				else:
					action: Action
					if line == "s":
						action = Action(ActionType.Selection)

					elif line == "Base":
						action = Action(ActionType.Base)

					elif line == "SingleMineral":
						action = Action(ActionType.Mineral)

					else:
						action = Action(ActionType.Hotkey)
						hotkey = Hotkey()
						hotkey.key = line[6]
						hotkey.action = HotkeyAction(int(line[7]))
						action.hotkey = hotkey

					interval.actions.append(action)
			games.append(g)
			# Limit to 10 for testing
			if c == 10:
				break
			c += 1
	return games
