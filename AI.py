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

            if res_cell not in AI.easy_map.unknown_res:
                all_messages.append((MessageType.RESOURCE, (res_cell), 0))

        my_cell = self.game.ant.getLocationCell()
        if my_cell.resource_value > 0 and self.am_i_allowed_to_tell(my_cell):
            all_messages.append((MessageType.MY_POS_on_RES,
                                 (my_cell.x, my_cell.y), 0))

        for invalid in AI.easy_map.to_invalid_res:
            if invalid not in AI.easy_map.invalidated_res:
                all_messages.append((MessageType.INVALIDATE_RESOURCE, invalid, 0))
        
        if len(all_messages) == 0:
            return None, 0
        return EasyMessage.pack_messages(all_messages)

    def random_walk(self):
        dist = 0
        while True:
            l = self.get_all_unvisited_cells_with_dist(dist)
            if l:
                return random.choice(l)
            dist += 1

    def get_all_unvisited_cells_with_dist(self, dist):
        l = []
        my_pos = (self.game.ant.currentX, self.game.ant.currentY)
        for x in range(-1 * dist, dist + 1):
            y = dist - abs(x)
            pos = AI.easy_map.get_easy_neighbor(my_pos, x, y)
            if not pos in AI.easy_map.visited_cells and not AI.easy_map.is_wall(pos):
                l.append(pos)
        return l

    def kargar_decide(self, me):
        resource = me.currentResource
        my_pos = (me.currentX, me.currentY)
        my_base = (self.game.baseX, self.game.baseY)
        AI.easy_map.visited_cells.add(my_pos)

        if resource.value > 0:  # TODO: age ja dasht bazam bardare
            self.direction = AI.easy_map.get_shortest_path(my_pos, my_base)[0]
            logger.info("base destination")
        else:
            res_pos, move = AI.easy_map.find_best_resource(my_pos)
            logger.info(f"resource destination: {res_pos}")
            self.direction = move
            if self.direction is None:
                res_pos = self.random_walk()
                self.direction = AI.easy_map.get_shortest_path(my_pos, res_pos)[0]
                logger.info("random destination")

        message, value = self.send_message()
        if value != 0:
            self.message = message
            self.value = value

    def sarbaz_decide(self, me):
        my_pos = (me.currentX, me.currentY)
        my_base = (self.game.baseX, self.game.baseY)
        AI.easy_map.visited_cells.add(my_pos)

        att_pos, move = AI.easy_map.find_best_attack_pos(my_pos)
        logger.info(f"attack destination: {att_pos}")
        self.direction = move
        print(move)
        if self.direction is None:
            res_pos = self.random_walk()
            self.direction = AI.easy_map.get_shortest_path(my_pos, res_pos)[0]
            logger.info("random destination")

        message, value = self.send_message()
        if value != 0:
            self.message = message
            self.value = value

    def log_stuff(self):
        self.print_all_map()
        me = self.game.ant
        logger.info(f"Turn: {AI.turn_num}")
        logger.info(f"my pos: {(me.currentX, me.currentY)}")
        logger.info(f"walls: {AI.easy_map.walls}")
        logger.info(f"breads: {AI.easy_map.bread}")
        logger.info(f"garss: {AI.easy_map.grass}")
        logger.info(f"unknown res: {AI.easy_map.unknown_res}")
        logger.info(f"defence cells: {AI.easy_map.defence_cells}")

    def turn(self) -> (str, int, int):
        AI.easy_map.update(self.game)
        me = self.game.ant
        ant_type = me.antType

        self.log_stuff()

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
