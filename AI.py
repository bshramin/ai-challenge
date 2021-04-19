from Model import *
import random
import json
from typing import *
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
RANGE = 5

class AI:

    def __init__(self):
        # Current Game State
        self.game: Game = None

        # Answer
        self.message: str = None
        self.direction: int = None
        self.value: int = None

    def get_manhatani_distance(self, x_mabda, y_mabda, x_maghsad, y_maghsad):
        return abs(x_mabda - x_maghsad) + abs(y_mabda - y_maghsad)

    def find_resource(self):
        best_destination = 6
        x_destination = self.game.ant.currentX
        y_destination = self.game.ant.currentY
        best_message = 0
        x_message = 0
        y_message = 0
        for i in range(-1 * RANGE, RANGE + 1): # inja range e yaro e
            for j in range(-1 * RANGE, RANGE + 1):
                if abs(i) + abs(j) > self.game.ant.viewDistance:
                    continue
                if self.game.ant.getNeightbourCell(i, j).resource_value > 0:
                    if best_destination > abs(i) + abs(j):
                        best_destination = abs(i) + abs(j)
                        x_destination = i
                        y_destination = j
                    value = (
                        self.game.ant.getNeightbourCell(i, j).resource_value + 100 -
                        self.get_manhatani_distance(
                            self.game.ant.currentX + i, self.game.ant.currentY + j, self.game.baseX, self.game.baseY
                        ))
                    if value > best_message:
                        best_message = value
                        x_message = self.game.ant.currentX + i
                        y_message = self.game.ant.currentY + j
        return x_destination, y_destination, best_destination, x_message, y_message, best_message

    def find_resource_for_others(self):
        best_message = 0
        x_message = 0
        y_message = 0
        for i in range(-5, 6):
            for j in range(-5, 6):
                if abs(i) + abs(j) > self.game.ant.viewDistance:
                    continue
                if self.game.ant.getNeightbourCell(i, j).resource_value > 0:
                    value = (
                            self.game.ant.getNeightbourCell(i, j).resource_value + 100 -
                            self.get_manhatani_distance(
                                self.game.ant.currentX + i, self.game.ant.currentY + j, self.game.baseX, self.game.baseY
                            ))
                    if value > best_message:
                        best_message = value
                        x_message = self.game.ant.currentX + i
                        y_message = self.game.ant.currentY + j
        return x_message, y_message, best_message

    def get_path(self, x, y):
        my_x = self.game.ant.currentX
        my_y = self.game.ant.currentY
        if y > my_y:
            if self.game.ant.getNeightbourCell(0, 1).type == 2:
                if x > my_x and self.game.ant.getNeightbourCell(1, 0).type != 2:
                    return Direction.RIGHT.value
                elif x < my_x and self.game.ant.getNeightbourCell(0, -1).type != 2:
                    return Direction.LEFT.value
                return Direction.RIGHT.value
            return Direction.DOWN.value
        if y < my_y:
            if self.game.ant.getNeightbourCell(0, -1).type == 2:
                if x > my_x and self.game.ant.getNeightbourCell(1, 0).type != 2:
                    return Direction.RIGHT.value
                elif x < my_x and self.game.ant.getNeightbourCell(0, -1).type != 2:
                    return Direction.LEFT.value
                return Direction.LEFT.value
            return Direction.UP.value
        if x > my_x:
            if self.game.ant.getNeightbourCell(1, 0).type == 2:
                if y > my_y and self.game.ant.getNeightbourCell(0, 1).type != 2:
                    return Direction.DOWN.value
                elif y < my_y and self.game.ant.getNeightbourCell(0, -1).type != 2:
                    return Direction.UP.value
                return Direction.UP.value
            return Direction.RIGHT.value
        if x < my_x:
            if self.game.ant.getNeightbourCell(-1, 0).type == 2:
                if y > my_y and self.game.ant.getNeightbourCell(0, 1).type != 2:
                    return Direction.DOWN.value
                elif y < my_y and self.game.ant.getNeightbourCell(0, -1).type != 2:
                    return Direction.UP.value
                return Direction.UP.value
            return Direction.LEFT.value
        return Direction.UP.value

    def get_next_step(self, position, goal):  # get_next_step((2,2),(5,6)) goal in vision
        visited_cells = []
        moves_list = [[]]
        cells = [position]
        while True:
            if len(cells) == 0:
                return None
            cell = cells[0]
            visited_cells.append(cell)
            moves = moves_list[0]
            del cells[0]
            del moves_list[0]
            if cell[0] == goal[0] and cell[1] == goal[1]:
                if len(moves) > 0:
                    return moves[0]
                else:
                    return None

            up_cell = (cell[0], cell[1] - 1)
            if up_cell not in visited_cells and (
                    (self.get_manhatani_distance(position[0], position[1], up_cell[0], up_cell[1]) > self.game.ant.viewDistance) or
                    (self.game.ant.getNeightbourCell(up_cell[0] - position[0], up_cell[1] - position[1]).type != 2)
            ):
                cells.append(up_cell)
                moves_list.append(moves + [Direction.UP.value])

            down_cell = (cell[0], cell[1] + 1)
            if down_cell not in visited_cells and (
                    (self.get_manhatani_distance(position[0], position[1], down_cell[0], down_cell[1]) > self.game.ant.viewDistance) or
                    (self.game.ant.getNeightbourCell(down_cell[0] - position[0], down_cell[1] - position[1]).type != 2)
            ):
                cells.append(down_cell)
                moves_list.append(moves + [Direction.DOWN.value])

            right_cell = (cell[0] + 1, cell[1])
            if right_cell not in visited_cells and (
                    (self.get_manhatani_distance(position[0], position[1], right_cell[0], right_cell[1]) > self.game.ant.viewDistance) or
                    (self.game.ant.getNeightbourCell(right_cell[0] - position[0], right_cell[1] - position[1]).type != 2)
            ):
                cells.append(right_cell)
                moves_list.append(moves + [Direction.RIGHT.value])

            left_cell = (cell[0] - 1, cell[1])
            if left_cell not in visited_cells and (
                    (self.get_manhatani_distance(position[0], position[1], left_cell[0], left_cell[1]) > self.game.ant.viewDistance) or
                    (self.game.ant.getNeightbourCell(left_cell[0] - position[0], left_cell[1] - position[1]).type != 2)
            ):
                cells.append(left_cell)
                moves_list.append(moves + [Direction.LEFT.value])

    def turn(self) -> (str, int, int):
        ant_type = self.game.ant.antType
        if int(ant_type) == 1:
            resource = self.game.ant.currentResource
            if resource.value > 0:
                self.direction = self.get_next_step(position=(self.game.ant.currentX, self.game.ant.currentY), goal=(self.game.baseX, self.game.baseY))
                x_message, y_message, value = self.find_resource_for_others()
            else:
                x, y, destination, x_message, y_message, value = self.find_resource()
                if destination < 6:
                    self.direction = self.get_next_step(position=(self.game.ant.currentX, self.game.ant.currentY), goal=(self.game.ant.currentX + x, self.game.ant.currentY + y))
                else:
                    chat_box = self.game.chatBox
                    destination = chat_box.allChats[-1].text.split(',')
                    x = int(destination[0])
                    y = int(destination[1])
                    if x and y:
                        self.direction = self.get_next_step(position=(self.game.ant.currentX, self.game.ant.currentY), goal=(x, y))
                    else:
                        self.direction = random.choice(list(Direction)).value

            if value != 0:
                self.message = str(x_message) + ',' + str(y_message)
                self.value = value
        else:
            x, y, destination, x_message, y_message, value = self.find_resource()
            if destination < 6:
                self.direction = self.get_next_step(position=(self.game.ant.currentX, self.game.ant.currentY),
                                                    goal=(self.game.ant.currentX + x, self.game.ant.currentY + y))
            else:
                chat_box = self.game.chatBox
                destination = chat_box.allChats[-1].text.split(',')
                x = int(destination[0])
                y = int(destination[1])
                if x and y:
                    self.direction = self.get_next_step(position=(self.game.ant.currentX, self.game.ant.currentY),
                                                        goal=(x, y))
                else:
                    self.direction = random.choice(list(Direction)).value
            if value != 0:
                self.message = str(x_message) + ',' + str(y_message)
                self.value = value
        logging.warning(self.direction)
        return self.message, self.value, self.direction
