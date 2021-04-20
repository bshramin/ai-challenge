import json
import logging
import os
import random
import time
from typing import *

from Easy_map import *
from Model import *

if not os.path.exists('ezlog'):
    os.makedirs('ezlog')

logging.basicConfig(filename=f'ezlog/ant{time.time()}.log',
                    filemode='w',
                    format='%(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


class AI:
    turn_num = 0
    easy_map = EasyMap()

    def __init__(self):
        # Current Game State
        self.game: Game = None
        AI.turn_num += 1

        # Answer
        self.message: str = None
        self.direction: int = None
        self.value: int = None

    def print_all_map(self):
        for j in range(self.game.mapHeight):
            line = ""
            for i in range(self.game.mapWidth):
                if self.game.ant.visibleMap.cells[i] is None:
                    return
                cell = self.game.ant.visibleMap.cells[i][j]
                if cell:
                    line = line + f"({cell.x},{cell.y})"
                else:
                    line = line + "(   )"
            logger.info(line)

    def send_message(self):
        my_base = (self.game.baseX, self.game.baseY)
        best_val = 0  # TODO: add priorities and calc best_val in proirity
        best_message = None
        for res_cell, res_val in {**AI.easy_map.bread, **AI.easy_map.grass}.items():
            if res_cell not in AI.easy_map.local_view:  # TODO: improve
                continue
            val = res_val + 100 - AI.easy_map.get_distance(res_cell, my_base)
            if val > best_val:  # TODO:check id already is in chatbox
                best_val = val
                best_message = str(x(res_cell)) + ',' + str(y(res_cell))
        return best_message, best_val

    def kargar_decide(self, me):
        resource = me.currentResource
        my_pos = (me.currentX, me.currentY)
        my_base = (self.game.baseX, self.game.baseY)

        if resource.value > 0: #TODO: age ja dasht bazam bardare
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
        self.print_all_map()

        me = self.game.ant
        ant_type = me.antType

        logger.info(f"Turn: {AI.turn_num}")
        logger.info(f"my pos: {(me.currentX, me.currentY)}")
        logger.info(f"walls: {AI.easy_map.walls}")
        logger.info(f"breads: {AI.easy_map.bread}")
        logger.info(f"garss: {AI.easy_map.grass}")

        if ant_type == AntType.KARGAR.value:
            self.kargar_decide(me)
        else:
            self.sarbaz_decide(me)

        logger.info(
            f"decide: { self.direction} - message: {self.message} - value: { self.value}")
        logger.info("")
        logger.info("")
        return self.message, self.value, self.direction
