from Model import Direction
from Model import *


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

    @staticmethod
    def get_distance(source_cell, dest_cell):
        return abs(x(source_cell) - x(dest_cell)) + abs(y(source_cell) - y(dest_cell))

    def update(self, game: Game):  # TODO: update from messages too
        self.game = game
        for i in range(-1 * game.viewDistance, game.viewDistance + 1):
            for j in range(-1 * game.viewDistance, game.viewDistance + 1):
                cell = game.ant.getNeightbourCell(i, j)
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
                return None

            cell = queue[0]
            moves = moves_list[0]
            del queue[0]
            del moves_list[0]
            if cell == dest_cell:
                if len(moves) > 0:
                    return moves[0]
                else:
                    return None

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
        min_dist = self.game.ant.viewDistance + 2  # TODO: maybe check outside of local too
        best_cell = None
        for res_cell, res_val in {**self.bread, **self.grass}.items():  # TODO: decide res_type
            # TODO: check res_value too
            dist = self.get_distance(source_cell, res_cell)
            if dist < min_dist:
                min_dist = dist
                best_cell = res_cell
        return best_cell

    def find_best_attack_pos(self, source_cell):  # TODO: check enemies
        return self.find_best_resource(source_cell)
