import json
import logging
import random
import time
from typing import *

from Easy_map import EasyMap
from Model import *

logging.basicConfig(filename=f'logs/instance{time.time()}.log',
                    filemode='w',
                    format='%(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


class AI:
    easy_map = EasyMap()

    def __init__(self):
        # Current Game State
        self.game: Game = None

        # Answer
        self.message: str = None
        self.direction: int = None
        self.value: int = None

    def print_all_map(self):
        for cells in self.game.ant.visibleMap.cells:
            if cells is None:
                return
            for cell in cells:
                if cell:
                    print(f"({cell.x},{cell.y})", end='')
                else:
                    print("(   )", end='')
            print()

    def send_message(self):
        # value = (
        #     self.game.ant.getNeightbourCell(i, j).resource_value + 100 -
        #     self.get_manhatani_distance(
        #         self.game.ant.currentX + i, self.game.ant.currentY +
        #         j, self.game.baseX, self.game.baseY
        #     ))
        # if value > best_message:
        #     best_message = value
        # str(x_message) + ',' + str(y_message)
        return 0, 0

    def kargar_decide(self, me):
        resource = me.currentResource
        my_pos = (me.currentX, me.currentY)
        my_base = (self.game.baseX, self.game.baseY)

        if resource.value > 0:
            self.direction = AI.easy_map.get_shortest_path(my_pos, my_base)
        else:
            res_pos = AI.easy_map.find_best_resource(my_pos)
            self.direction = AI.easy_map.get_shortest_path(my_pos, res_pos)
            if self.direction is None:
                self.direction = random.choice(list(Direction)).value

        message, value = self.send_message()
        if value != 0:
            self.message = message
            self.value = value

    def sarbaz_decide(self, me):
        my_pos = (me.currentX, me.currentY)
        my_base = (self.game.baseX, self.game.baseY)

        att_pos = AI.easy_map.find_best_attack_pos(my_pos)
        self.direction = AI.easy_map.get_shortest_path(my_pos, att_pos)
        if self.direction is None:
            self.direction = random.choice(list(Direction)).value

        message, value = self.send_message()
        if value != 0:
            self.message = message
            self.value = value

    def turn(self) -> (str, int, int):
        AI.easy_map.update(self.game)
        # self.print_all_map()

        me = self.game.ant
        ant_type = me.antType

        if ant_type == AntType.KARGAR.value:
            self.kargar_decide(me)
        else:
            self.sarbaz_decide(me)

        print("decide:", self.direction, "- message: ",
              self.message, "- value: ", self.value)
        return self.message, self.value, self.direction
