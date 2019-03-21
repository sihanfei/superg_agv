# coding = utf-8

import numpy as np
import JsonFormat as jft
import matplotlib.pyplot as plt


class CalcRefLine:
    def __init__(self):
        pass

    def makeConnectMap(self, entities_dict,
                       threshold):  # currentEntityID : (nextID0, ..., nextIDn)
        # 取任意终点,计算其他起点与它之间的距离,
        # 如果小于阈值,则认为是同一点,
        # 把该点对应的id作为键,把其他id作为值,保存到connect_map_dict中
        connect_map_dict = {}
        end_points = []
        start_points = []
        key_list = []
        # 获取点与键
        for _, key in enumerate(entities_dict):
            key_list.append(key)
            end_points.append(entities_dict[key].end)
            start_points.append(entities_dict[key].start)
        # 计算并比较距离
        for i in range(len(end_points)):
            connect_value_list = []
            for j in range(len(start_points)):
                distance = self.calcPointsDistance(end_points[i],
                                                   start_points[j])
                if distance < threshold:
                    connect_value_list.append(j)
            connect_map_dict[key_list[i]] = connect_value_list
            print("makConnectMap: connect_dict={}:{}".format(
                key_list[i], connect_value_list))
        return connect_map_dict

    def calcPointsDistance(self, p0, p1):
        distance = np.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
        return distance

    def getRefLine(self, entity):
        pass
        ref_line = []
        ps = entity.start
        pe = entity.end

        return ref_line


if __name__ == "__main__":
    line_map_obj = jft.readLineMapFromJson('Line_Map.json')
    entities_dict = {}
    # read data
    for _, key in enumerate(line_map_obj):
        if key == 0:
            print("main: {}:{}".format(key, line_map_obj[key][0]))
        entity = jft.LineEntity(line_map_obj[key][0], line_map_obj[key][1],
                                line_map_obj[key][2], line_map_obj[key][3],
                                line_map_obj[key][4], line_map_obj[key][5])
        entities_dict[key] = entity
    # calc
    calc_ref_line = CalcRefLine()
    connect_map_dict = calc_ref_line.makeConnectMap(entities_dict, 2)

    for _, key in entities_dict:
        entity = entities_dict[key]
        ref_line = calc_ref_line.getRefLine(entity)
