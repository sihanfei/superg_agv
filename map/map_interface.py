# coding = utf-8

import numpy as np
import JsonFormat as jft
import matplotlib.pyplot as plt
import scipy.spatial as spt


class CalcRefLine:
    def __init__(self):
        pass

    def makeConnectMap(self, entities_dict,
                       threshold):  # currentEntityID : (nextID0, ..., nextIDn)
        # 取任意终点,计算其他起点与它之间的距离,
        # 如果小于阈值,则认为是同一点,
        # 把该点对应的id作为键,把其他id作为值,保存到connect_map_dict中
        connect_map_dict = {}
        # 获取点与键
        for _, keyE in enumerate(entities_dict):
            endp = entities_dict[keyE].end
            connect_value_list = []
            for _, keyS in enumerate(entities_dict):
                startp = entities_dict[keyS].start
                distance = self.calcPointsDistance(endp, startp)
                if distance < threshold:
                    connect_value_list.append(keyS)
            connect_map_dict[keyE] = connect_value_list
            print("makConnectMap: connect_dict={}:{}".format(
                keyE, connect_value_list))
        return connect_map_dict

    def calcPointsDistance(self, p0, p1):
        distance = np.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
        return distance

    def getRefLine(self, entity):
        scatter_point = []
        if entity.linetype == 'LINE':
            start_point, end_point = entity.start, entity.end
            d = self.calcPointsDistance(start_point, end_point)
            delta_x = (end_point[0] - start_point[0]) / d
            delta_y = (end_point[1] - start_point[1]) / d
            if delta_x == 0 and delta_y == 0:
                x = start_point[0]
                y = start_point[1]
            elif delta_x != 0 and delta_y == 0:
                x = np.arange(start_point[0], end_point[0] + delta_x, delta_x)
                y = np.ones(x.shape) * start_point[1]
            elif delta_x == 0 and delta_y != 0:
                y = np.arange(start_point[1], end_point[1] + delta_y, delta_y)
                x = np.ones(y.shape) * start_point[0]
            else:
                x = np.arange(start_point[0], end_point[0], delta_x)
                y = np.arange(start_point[1], end_point[1], delta_y)
            np.insert(x, -1, end_point[0])
            np.insert(y, -1, end_point[1])
            for i in range(len(x)):
                ref_point = jft.RefPointPara()
                ref_point.setCuv(0)
                ref_point.setGcuv(0)
                ref_point.setWidth(tuple([2, 2]))
                if (x[1] - x[0]) == 0:
                    ref_point.setTheta((y[1] - y[0]) * np.pi / 2)
                else:
                    ref_point.setTheta(
                        np.arctan((y[1] - y[0]) / (x[1] - x[0])))
                distance_s = np.sqrt((x[i] - x[0])**2 + (y[i] - y[0])**2)
                ref_point.setPoint(tuple([x[i], y[i]]))
                ref_point.setS(distance_s)
                scatter_point.append(ref_point)
        elif entity.linetype == 'ARC':
            center_point = entity.center
            radius = entity.radius
            start_angle = entity.angle[0]
            end_angle = entity.angle[1]
            length = radius * np.abs(end_angle - start_angle)
            delta_angle = (end_angle - start_angle) / length  # 按照弧长为基准转换
            angle_array = np.arange(start_angle, end_angle + delta_angle,
                                    delta_angle)
            x = np.cos(angle_array) * radius + center_point[0]
            y = np.sin(angle_array) * radius + center_point[1]
            for i in range(len(x)):
                ref_point = jft.RefPointPara()
                ref_point.setCuv(1 / radius)
                ref_point.setWidth(tuple([2, 2]))
                distance_s = radius * (angle_array[i] - angle_array[0])
                ref_point.setPoint(tuple([x[i], y[i]]))
                ref_point.setS(distance_s)
                if i != 0:
                    ref_point.setGcuv(ref_point.cuv / distance_s)
                else:
                    ref_point.setGcuv(0)
                ref_point.setTheta(angle_array[i] - np.pi / 2)
                scatter_point.append(ref_point)
        else:
            pass
        print('scatterLine:point:s={}, e={}, num={}'.format(
            scatter_point[0].point, scatter_point[-1].point,
            len(scatter_point)))
        return list(scatter_point)


class MapService:
    def __init__(self):
        pass

    def makePointsTree(self, ref_line):
        points = []
        for i in range(len(ref_line)):
            points.append(ref_line[i].point)
        atree = spt.KDTree(points)
        return atree

    def makeTreeDict(self, ref_line_dict):
        tree_dict = {}
        for _, key in enumerate(ref_line_dict):
            atree = self.makePointsTree(ref_line_dict[key])
            tree_dict[key] = atree
        return tree_dict

    def getIDbyXYZ(self, xyz, tree_dict):
        ref_line_id = 0
        min_dist = 1000
        min_point = []
        for _, key in enumerate(tree_dict):
            distance, index = tree_dict[key].query(xyz)
            if distance <= min_dist:
                min_dist = distance
                ref_line_id = key
                min_point = tree_dict[key].data[index]
        return ref_line_id, min_dist, min_point

    def getNextIDbyID(self, currentID, connect_map_dict):
        return connect_map_dict[currentID]

    def getRefLinebyID(self, currentID, ref_line_dict):
        return ref_line_dict[currentID]


if __name__ == "__main__":
    line_map_obj = jft.readLineMapFromJson('Line_Map.json')
    entities_dict = {}
    # read data from file
    for _, key in enumerate(line_map_obj):
        if key == 0:
            print("main: {}:{}".format(key, line_map_obj[key][0]))
        entity = jft.LineEntity(line_map_obj[key][0], line_map_obj[key][1],
                                line_map_obj[key][2], line_map_obj[key][3],
                                line_map_obj[key][4], line_map_obj[key][5])
        entities_dict[key] = entity
    # connectmap
    calc_ref_line = CalcRefLine()
    connect_map_dict = calc_ref_line.makeConnectMap(entities_dict, 2)
    # ref_line
    ref_line_dict = {}
    for _, key in enumerate(entities_dict):
        entity = entities_dict[key]
        ref_line = calc_ref_line.getRefLine(entity)
        ref_line_dict[key] = ref_line
    # 启动地图服务
    map_service = MapService()
    tree_dict = map_service.makeTreeDict(ref_line_dict)
    print(map_service.getIDbyXYZ([100, 100], tree_dict))
