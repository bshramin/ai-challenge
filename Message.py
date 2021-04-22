import logging

from Config import *

logger = logging.getLogger(__name__)


class MessageType:  # also major_priority
    RESOURCE = 0
    MY_POS_on_RES = 1
# TODO: add undo messages


class EasyMessage:
    '''
    message: (type,pos),priority
    priority = min_proirity + major_priority
    '''

    major_priority_map = {
        MessageType.RESOURCE: 100,
        MessageType.MY_POS_on_RES: 200,
    }

    @staticmethod
    def pack_messages(message_objects):  # type,(x,y),min_priority
        message_pack = []
        for mtype, mpos, mpriority in message_objects:
            mval = f"{mtype},{mpos[0]},{mpos[1]}"
            priority = EasyMessage.major_priority_map[mtype] + mpriority
            message_pack.append((mval, priority))

        sorted_pack = sorted(message_pack, key=lambda k: k[1], reverse=True)
        message_pack_str = sorted_pack[0][0]
        message_sum_val = sorted_pack[0][1]
        for message in sorted_pack[1:]:
            if len(message_pack_str + message[0]) < max_com_length:
                message_pack_str += "|" + message[0]
                message_sum_val += message[1]

        logging.info(f"all messages: {sorted_pack}")
        return message_pack_str, message_sum_val

    @staticmethod
    def unpack_message(messages_str):
        message_objects = dict()
        for message_str in messages_str.split('|'):
            mtype, mpos_x, mpos_y = message_str.split(',')
            if mtype not in message_objects:
                message_objects[mtype] = []
            message_objects[mtype].append((mpos_x, mpos_y))
        return message_objects