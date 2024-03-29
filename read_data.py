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


def read_file(filename: str, max_items: int, label_present: bool) -> [Game]:
	games: [Game] = []
	with open(filename, "r") as file:

		line_nb = 0
		for line in file:
			if line_nb > max_items:
				break
			line_nb += 1

			line_data = line.split(',')

			g = Game()
			if label_present:
				g.playerId = line_data[0]
			g.race = Race[line_data[1 if label_present else 0].strip()]
			g.intervals = []

			interval = ActionInterval(0)
			g.intervals.append(interval)
			start = 2 if label_present else 1
			for i in range(start, len(line_data)):
				line = line_data[i].strip()
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
						hotkey.key = int(line[6])
						hotkey.action = HotkeyAction(int(line[7]))
						action.hotkey = hotkey

					interval.actions.append(action)
			games.append(g)
	return games
