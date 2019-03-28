# coding = utf-8

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as ln
import PIL.Image as PIImg
import dxfgrabber as grb
import copy as cp
import scipy.spatial as spt
import json

from gps_point import GPSPoint
import JsonFormat as jft


class LineEntity:
    def __init__(self):
        self.linetype = []
        self.start = []
        self.end = []
        self.angles = []
        self.center = []
        self.radius = []
        self.length = []

    def setLineType(self, line_type):
        self.linetype = line_type

    def setStart(self, start):
        self.start = start

    def setEnd(self, end):
        self.end = end

    def setAngles(self, angles):
        self.angles = angles

    def setCenter(self, center):
        self.center = center

    def setRadius(self, radius):
        self.radius = radius

    def setLength(self, length):
        self.length = length

    def initFromDXF(self, orig_dxf_entity, scale, bias):
        dxf_entity = self.__DXFEntityReinit__(orig_dxf_entity, scale, bias)
        self.__toLineEntity__(dxf_entity)
        self.scale = scale
        self.bias = bias

    # 将dxf中的mm转换为m, 并根据图片的缩放\平移需求,对entity进行参数的重置
    def __DXFEntityReinit__(self, orig_DXF_entity, scale, bias):
        dxf_entity = cp.deepcopy(orig_DXF_entity)
        # dxf_entity = orig_DXF_entity
        if orig_DXF_entity.dxftype == 'LINE':
            dxf_entity.start = GPSPoint.shiftPoint(orig_DXF_entity.start,
                                                   1 / 1000, scale, bias)
            dxf_entity.end = GPSPoint.shiftPoint(orig_DXF_entity.end, 1 / 1000,
                                                 scale, bias)
        elif orig_DXF_entity.dxftype == 'ARC':
            dxf_entity.center = GPSPoint.shiftPoint(orig_DXF_entity.center,
                                                    1 / 1000, scale, bias)
            dxf_entity.radius = orig_DXF_entity.radius / 1000 * scale
            dxf_entity.start_angle = orig_DXF_entity.start_angle * np.pi / 180
            dxf_entity.end_angle = orig_DXF_entity.end_angle * np.pi / 180
            if dxf_entity.start_angle > dxf_entity.end_angle:  # 为防止画图出错,强制让start小于end
                dxf_entity.start_angle = dxf_entity.start_angle - 2 * np.pi
        return dxf_entity

    # 将dxfentity转换为lineentity
    def __toLineEntity__(self, dxf_entity):
        """
        change dxf_entity to line_entity
        return : line_entity
        """
        startp, endp = self.__getEndPoints__(dxf_entity)
        length = self.__getLength__(dxf_entity)
        if dxf_entity.dxftype == 'LINE':
            angles = [0, 0]
            center = [0, 0]
            radius = 0
        elif dxf_entity.dxftype == 'ARC':
            angles = [dxf_entity.start_angle, dxf_entity.end_angle]
            center = dxf_entity.center
            radius = dxf_entity.radius
        self.setLineType(dxf_entity.dxftype)
        self.setStart(startp)
        self.setEnd(endp)
        self.setAngles(angles)
        self.setCenter(center)
        self.setRadius(radius)
        self.setLength(length)

    # 获取dxf_entity的端点
    def __getEndPoints__(self, dxf_entity):
        startp = []
        endp = []
        if dxf_entity.dxftype == 'LINE':
            startp = dxf_entity.start
            endp = dxf_entity.end
        elif dxf_entity.dxftype == 'ARC':
            startp = tuple(
                np.array(dxf_entity.center) + np.array([
                    np.cos(dxf_entity.start_angle),
                    np.sin(dxf_entity.start_angle)
                ]) * dxf_entity.radius)
            endp = tuple(
                np.array(dxf_entity.center) + np.array([
                    np.cos(dxf_entity.end_angle),
                    np.sin(dxf_entity.end_angle)
                ]) * dxf_entity.radius)
        return startp, endp

    # 根据dxfentity参数,计算entity的线段/弧线长度
    def __getLength__(self, dxf_entity):
        length = 0
        if dxf_entity.dxftype == 'LINE':
            sp, ep = self.__getEndPoints__(dxf_entity)
            length = GPSPoint.calcTwoPointsDistance(sp, ep)
            pass
        elif dxf_entity.dxftype == 'ARC':
            length = dxf_entity.radius * (
                dxf_entity.end_angle - dxf_entity.start_angle)
            pass
        else:
            pass
        return length

    # 根据dxf_entity参数,计算全部离散点GPS坐标
    def scatterGPSPoints(self):
        if self.linetype == 'LINE':
            sp, ep = self.start, self.end
            length = self.length
            delta_x = (ep[0] - sp[0]) / length
            delta_y = (ep[1] - sp[1]) / length
            if delta_y == 0:
                xlist = np.arange(sp[0], ep[0], delta_x)
                ylist = np.ones(xlist.shape) * sp[1]
            elif delta_x == 0:
                ylist = np.arange(sp[1], ep[1], delta_y)
                xlist = np.ones(ylist.shape) * sp[0]
            else:
                xlist = np.arange(sp[0], ep[0], delta_x)
                ylist = np.arange(sp[1], ep[1], delta_y)
            points = tuple(zip(xlist, ylist))
            # print('LineEntity: scatter: line points={}'.format(
            #     (self.start, self.end, self.length)))
        elif self.linetype == 'ARC':
            delta_angle = (self.angles[1] - self.angles[0]) / np.abs(
                self.angles[1] - self.angles[0]) / self.radius  # 按照弧长1m为基准转换
            angle_list = np.arange(self.angles[0], self.angles[1], delta_angle)
            # points = np.array([np.cos(angle_list),
            #           np.sin(angle_list)
            #           ]) * self.dxf_entity.radius + self.dxf_entity.center
            xlist = np.cos(angle_list) * self.radius + self.center[0]
            ylist = np.sin(angle_list) * self.radius + self.center[1]
            points = tuple(zip(xlist, ylist))
            # print('LineEntity: scatter: arc points={}'.format(self.angles))
        else:
            points = []
            pass
        return points

    # 根据
    def draw(self, **kwds):
        points = self.scatterGPSPoints()
        [x, y] = np.array(tuple((zip(*points))))
        line = ln.Line2D(x, y, **kwds)
        return line

    def changeEPTurn(self):
        if self.linetype == 'ARC':
            self.angles[0], self.angles[1] = self.angles[1], self.angles[0]
            # if self.angles[1] < self.angles[0]:
            #     self.angles[1] = self.angles[1] + 2 * np.pi
            #     print('changeEPTurn: angle:{}'.format(self.angles))
        elif self.linetype == 'LINE':
            self.start, self.end = self.end, self.start

    def isEqual(self, line_entity):
        if self.linetype != line_entity.linetype:
            return False
        else:
            if line_entity.linetype == 'LINE':
                d0 = GPSPoint.calcTwoPointsDistance(self.start,
                                                    line_entity.start)
                d1 = GPSPoint.calcTwoPointsDistance(self.end, line_entity.end)
                d2 = GPSPoint.calcTwoPointsDistance(self.start,
                                                    line_entity.end)
                d3 = GPSPoint.calcTwoPointsDistance(self.end,
                                                    line_entity.start)
                if (d0 == d2 and d1 == d3) or (d0 == d3 and d1 == d2):
                    return True
                else:
                    return False
            elif line_entity.linetype == 'ARC':
                dxf_center = np.array(self.center)
                dxf_radius = self.radius
                d0 = GPSPoint.calcTwoPointsDistance(dxf_center,
                                                    line_entity.center)
                if (d0 == 0) and ((
                    (dxf_radius - line_entity.radius) / dxf_radius) == 0):
                    return True
                else:
                    return False
                pass
            else:
                return False


if __name__ == "__main__":
    img1 = PIImg.open('../data/map/zhenjiang/zhenjiang.bmp')
    npimg1 = np.array(img1)
    npimg1 = npimg1[-1:0:-1, :, :]
    scale = 1 / 0.116
    bias = [-18.75, +0.75]
    # xyz_map = (xyz_map - bias) * scale  # 针对镇江地图的偏移

    # 准备绘图
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(npimg1, origin='lower', zorder=0)
    ax.autoscale(False)

    # 读取dxf文件
    dxf_object = grb.readfile('../data/map/zhenjiang/zhenjiang.dxf')

    num = 0
    board_points = []
    for entity in dxf_object.entities:
        if entity.layer == 'ref_line':
            num = num + 1
            entity_in_map = LineEntity()
            entity_in_map.initFromDXF(entity, scale, bias)
            line = entity_in_map.draw(color='r')
            ax.add_line(line)
        if entity.layer == 'board':
            entity_in_map = LineEntity()
            entity_in_map.initFromDXF(entity, scale, bias)
            if entity_in_map.linetype == 'ARC':
                entity_in_map.changeEPTurn()
                print('main: entity_in_map.center:{}'.format(
                    entity_in_map.angles))
            board_line = entity_in_map.draw(color='g')
            ax.add_line(board_line)
            points = entity_in_map.scatterGPSPoints()
            board_points.extend(points)
    board_points_tree = spt.KDTree(board_points)
    data = input('x, y = ')
    value = data.split(',')
    if len(value) == 2:
        point = [float(num) for num in value]
    else:
        point = [0, 0]
    # 显示找到的所有点
    near_points = board_points_tree.query_ball_point(point, 8 * scale)

    for ind in near_points:
        value = board_points_tree.data[ind]
        pline = ln.Line2D([value[0]], [value[1]], marker='.', color='k')
        ax.add_line(pline)

    theta = float(input('方向角:'))
    # 获取宽度与对应点
    width, points, angles = GPSPoint.getWidthinP(point, 8 * scale, theta,
                                                 board_points_tree)
    print('width, points, angles = {}, {}, {}'.format(
        width, points,
        np.array(angles) * 180 / np.pi))

    pline = ln.Line2D([points[0][0], points[1][0]],
                      [points[0][1], points[1][1]],
                      color='r',
                      marker='*',
                      zorder=100)
    ax.add_line(pline)

    pline = ln.Line2D([point[0]], [point[1]], marker='o')
    ax.add_line(pline)

    plt.show()
