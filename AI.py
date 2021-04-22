import logging
import os
import random
import time

from Config import *
from Easy_map import *
from Message import *
from Model import *

if not os.path.exists('ezlog'):
    os.makedirs('ezlog')

time_seed = int(time.time())
logging.basicConfig(filename=f'ezlog/ant{time_seed}.log',
                    filemode='w',
                    format='%(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


class AI:
    turn_num = 0
    easy_map = EasyMap()
    random.seed(time_seed)

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

    def am_i_allowed_to_tell(self, cell):
        me = self.game.ant
        for ant in cell.ants:
            if ant.antType == AntType.SARBAAZ.value and ant.antTeam == AntTeam.ALLIED.value:
                if me.antType == AntType.KARGAR:
                    return False
                elif random.random() < 0.4:
                    return False
        return True

    def send_message(self):
        my_base = (self.game.baseX, self.game.baseY)
        best_val = 0
        all_messages = []

        local_resources = {**AI.easy_map.bread, **AI.easy_map.grass}
        for res_cell, res_val in local_resources.items():
            if res_cell not in AI.easy_map.local_view:  # TODO: improve
                continue

            val = res_val + 2 * map_size - \
                AI.easy_map.get_distance(res_cell, my_base)
            if res_cell in AI.easy_map.unknown_res:
                val -= 60

            all_messages.append((MessageType.RESOURCE, (res_cell), val))
        my_cell = self.game.ant.getLocationCell()
        if my_cell.resource_value > 0 and self.am_i_allowed_to_tell(my_cell):
            val = 2 * map_size - AI.easy_map.get_distance(res_cell, my_base)
            all_messages.append((MessageType.MY_POS_on_RES,
                                 (my_cell.x, my_cell.y), val))
        if len(all_messages) == 0:
            return None, 0
        return EasyMessage.pack_messages(all_messages)

    def kargar_decide(self, me):
        resource = me.currentResource
        my_pos = (me.currentX, me.currentY)
        my_base = (self.game.baseX, self.game.baseY)

        if resource.value > 0:  # TODO: age ja dasht bazam bardare
            self.direction = AI.easy_map.get_shortest_path(my_pos, my_base)[0]
            logger.info("base destination")
        else:
            res_pos, move = AI.easy_map.find_best_resource(my_pos)
            logger.info(f"resource destination: {res_pos}")
            self.direction = move
            print(move)
            if self.direction is None:
                self.direction = random.choice(list(Direction)[1:]).value
                logger.info("random destination")

        message, value = self.send_message()
        if value != 0:
            self.message = message
            self.value = value

    def sarbaz_decide(self, me):
        my_pos = (me.currentX, me.currentY)
        my_base = (self.game.baseX, self.game.baseY)

        att_pos, move = AI.easy_map.find_best_attack_pos(my_pos)
        logger.info(f"attack destination: {att_pos}")
        self.direction = move
        print(move)
        if self.direction is None:
            self.direction = random.choice(list(Direction)[1:]).value
            logger.info("random destination")

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
        logger.info(f"unknown res: {AI.easy_map.unknown_res}")
        logger.info(f"defence cells: {AI.easy_map.defence_cells}")

        try:
            if ant_type == AntType.KARGAR.value:
                self.kargar_decide(me)
            else:
                self.sarbaz_decide(me)
        except Exception as e:
            logger.info("***EXCEPTION***")
            logger.exception(e)

        logger.info(
            f"decide: { self.direction} - message: {self.message} - value: { self.value}")
        logger.info("")
        logger.info("")
        return self.message, self.value, self.direction
