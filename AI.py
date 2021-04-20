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

    def kargar_decide(self):
        resource = self.game.ant.currentResource
        if resource.value > 0:
            self.direction = AI.easy_map.get_shortest_path(position=(
                self.game.ant.currentX, self.game.ant.currentY), goal=(self.game.baseX, self.game.baseY))
            x_message, y_message, value = self.find_resource_for_others()
        else:
            x, y, destination, x_message, y_message, value = self.find_resource()
            if destination < 6:
                self.direction = self.get_next_step(position=(self.game.ant.currentX, self.game.ant.currentY), goal=(
                    self.game.ant.currentX + x, self.game.ant.currentY + y))
            else:
                chat_box = self.game.chatBox
                destination = chat_box.allChats[-1].text.split(',')
                x = int(destination[0])
                y = int(destination[1])
                if x and y:
                    self.direction = self.get_next_step(
                        position=(self.game.ant.currentX, self.game.ant.currentY), goal=(x, y))
                else:
                    self.direction = random.choice(list(Direction)).value

        if value != 0:
            self.message = str(x_message) + ',' + str(y_message)
            self.value = value

    def sarbaz_decide(self):
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

    def turn(self) -> (str, int, int):
        AI.easy_map.update(self.game)
        self.print_all_map()
        
        me = self.game.ant
        ant_type = me.antType
        my_pos = (me.currentX, me.currentY)

        print("mypos: ", my_pos)
        print("walls: ", AI.easy_map.walls)

        self.direction = AI.easy_map.get_shortest_path(my_pos, (9, 9))
        # if ant_type == AntType.KARGAR.value:
        #     self.kargar_decide()
        # else:
        #     self.sarbaz_decide()
        print("dir: ", self.direction)
        return self.message, self.value, self.direction
