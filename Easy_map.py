import logging

from Config import *
from Message import *
from Model import *

logger = logging.getLogger(__name__)


def x(ez_cell):
    return ez_cell[0]


def y(ez_cell):
    return ez_cell[1]


class EasyMap():
    def __init__(self):
        self.game: Game = None

        self.local_view = set()
        self.walls = set()
        self.bread = dict()
        self.grass = dict()
        self.unknown_res = set()
        self.defence_cells = set()
        self.visited_cells = set()

    @staticmethod
    def get_distance(source_cell, dest_cell):
        return abs(x(source_cell) - x(dest_cell)) + abs(y(source_cell) - y(dest_cell))

    def update(self, game: Game):
        self.game = game
        self._update_from_messages()
        self._update_from_local_view()

    def _update_from_messages(self):
        # TODO:IMPROVEE
        for chat in self.game.chatBox.allChats[-1 * max_com_per_turn:]:
            message_str = chat.text
            messages = EasyMessage.unpack_message(message_str)
            self.defence_cells.update(
                messages.get(MessageType.MY_POS_on_RES, []))
            self.unknown_res.update(messages.get(MessageType.RESOURCE, []))

    def _update_from_local_view(self):
        for i in range(-1 * self.game.viewDistance, self.game.viewDistance + 1):
            for j in range(-1 * self.game.viewDistance, self.game.viewDistance + 1):
                cell = self.game.ant.getNeightbourCell(i, j)
                if cell is None:
                    continue

                easy_cell = (cell.x, cell.y)
                self.local_view.add(easy_cell)

                if cell.type == CellType.WALL.value:
                    self.walls.add(easy_cell)
                elif cell.resource_value > 0:
                    if cell.resource_type == ResourceType.BREAD.value:
                        self.bread[easy_cell] = cell.resource_value
                    else:
                        self.grass[easy_cell] = cell.resource_value
                else:
                    self.bread.pop(easy_cell, None)
                    self.grass.pop(easy_cell, None)
                    self.unknown_res.discard(easy_cell)
                    self.defence_cells.discard(easy_cell)

    def get_easy_neighbor(self, source_cell, dx, dy):
        cell_x = (x(source_cell) + dx) % self.game.mapWidth
        cell_y = (y(source_cell) + dy) % self.game.mapHeight
        return (cell_x, cell_y)

    def is_wall(self, cell):
        return cell in self.walls

    def get_shortest_path(self, source_cell, dest_cell):
        queue = [source_cell]
        visited = []
        moves_list = [[]]

        visited.append(source_cell)
        while True:
            if len(queue) == 0:
                return []

            cell = queue[0]
            moves = moves_list[0]
            del queue[0]
            del moves_list[0]
            if cell == dest_cell:
                if len(moves) > 0:
                    return moves
                else:
                     return [Direction.CENTER.value]

            dir_to_cell = {
                Direction.UP.value: self.get_easy_neighbor(cell, 0, -1),
                Direction.DOWN.value: self.get_easy_neighbor(cell, 0, 1),
                Direction.RIGHT.value: self.get_easy_neighbor(cell, 1, 0),
                Direction.LEFT.value: self.get_easy_neighbor(cell, -1, 0),
            }

            for cdir, cell in dir_to_cell.items():
                if cell not in visited and not self.is_wall(cell):
                    visited.append(cell)
                    queue.append(cell)
                    moves_list.append(moves + [cdir])

    def find_best_resource(self, source_cell):
        # TODO: maybe check outside of local too
        min_dist = map_size
        best_cell = None
        best_move = None
        # TODO: decide res_type
        for res_cell, res_val in {**self.bread, **self.grass}.items():
            # TODO: check res_value too
            moves = self.get_shortest_path(source_cell, res_cell)
            dist = len(moves)
            if dist > 0 and dist < min_dist:
                min_dist = dist
                best_cell = res_cell
                best_move = moves[0]

        if best_cell is None:
            for res_cell in self.unknown_res:
                moves = self.get_shortest_path(source_cell, res_cell)
                dist = len(moves)
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    best_cell = res_cell
                    best_move = moves[0]

        return best_cell, best_move

    def find_best_attack_pos(self, source_cell):  # TODO: check enemies for attack
        my_base = (self.game.baseX, self.game.baseY)
        min_dist = map_size
        best_cell = None
        best_move = None

        for def_cell in self.defence_cells:
            moves = self.get_shortest_path(source_cell, def_cell)
            dist = len(moves)
            if dist > 0 and dist < min_dist:
                min_dist = dist
                best_cell = def_cell
                best_move = moves[0]

        if best_cell is None:
            best_cell, best_move = self.find_best_resource(source_cell)

        return best_cell, best_move
