import sys
sys.path.append("..")

import numpy as np
import scipy.spatial as spt
import common.JsonFormat as jft
import csv as csv


def getNextIDbyID(connect_map_dict, id):
    return connect_map_dict[id]


def getRefLineLengthbyID(ref_line_dict, id):
    return ref_line_dict[id][-1][2]


def getConnectMapFromJson(filename):
    connect_map_dict = {}
    try:
        fp = open(filename, 'r')
        connect_map = csv.reader(fp)
        for item in connect_map:
            value = []
            for i in range(2, len(item)):
                value.append(item[i])
            connect_map_dict[item[0]] = value
    except FileExistsError:
        return False
    finally:
        fp.close()
    return connect_map_dict


def getRefLineMapFromJson(filename):
    ref_line_map_dict = {}
    try:
        fp = open(filename, 'r')
        ref_line_map = csv.reader(fp)
        for item in ref_line_map:
            point = jft.RefPointPara(
                tuple([item[1], item[2]]),
                tuple([item[1], item[2]]),
                item[1], item[]
            )
            ref_line_id = item[0]
            ref_line_map_dict[item[0]] = value
    except FileExistsError:
        return False
    finally:
        fp.close()
    return ref_line_map_dict


if __name__ == "__main__":
    file = "../data/map/zhenjiang/connect_map.json"
    connect_map_dict = getConnectMapFromJson(file)
    for _, key in enumerate(connect_map_dict):
        print('main:{}:{}'.format(key, connect_map_dict[key]))
