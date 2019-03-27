# coding = utf-8

import numpy as np
from gps_point import GPSPoint as gp
import JsonFormat as jft
import matplotlib.pyplot as plt
import matplotlib.lines as ln
import PIL.Image as PIImg
import dxfgrabber as grb
import copy as cp
import scipy.spatial as spt
import json


class EntityinMap:  # dxf中实体对象
    def __init__(self, dxf_entity, scale, bias):
        self.dxf_entity = self.DXFEntityReinit(dxf_entity, scale, bias)
        self.scale = scale
        self.bias = bias
        return

    # 将dxf中的mm转换为m, 并根据图片的缩放\平移需求,对entity进行参数的重置
    def DXFEntityReinit(self, orig_DXF_entity, scale, bias):
        dxf_entity = cp.deepcopy(orig_DXF_entity)
        # dxf_entity = orig_DXF_entity
        if orig_DXF_entity.dxftype == 'LINE':
            dxf_entity.start = gp.shiftPoint(orig_DXF_entity.start, 1 / 1000,
                                             scale, bias)
            dxf_entity.end = gp.shiftPoint(orig_DXF_entity.end, 1 / 1000,
                                           scale, bias)
        elif orig_DXF_entity.dxftype == 'ARC':
            dxf_entity.center = gp.shiftPoint(orig_DXF_entity.center, 1 / 1000,
                                              scale, bias)
            dxf_entity.radius = orig_DXF_entity.radius / 1000 * scale
            dxf_entity.start_angle = orig_DXF_entity.start_angle * np.pi / 180
            dxf_entity.end_angle = orig_DXF_entity.end_angle * np.pi / 180
            if dxf_entity.start_angle > dxf_entity.end_angle:  # 为防止画图出错,强制让start小于end
                dxf_entity.start_angle = dxf_entity.start_angle - 2 * np.pi
        return dxf_entity

    # 将dxfentity转换为lineentity
    def toLineEntity(self):
        startp, endp = self.getEndPoints()
        length = self.getLength()
        if self.dxf_entity.dxftype == 'LINE':
            angle = [0, 0]
            center = [0, 0]
            radius = 0
        elif self.dxf_entity.dxftype == 'ARC':
            angle = [self.dxf_entity.start_angle, self.dxf_entity.end_angle]
            center = self.dxf_entity.center
            radius = self.dxf_entity.radius
        line_entity = jft.LineEntity(self.dxf_entity.linetype, startp, endp,
                                     angle, center, radius, length)
        return line_entity

    # 获取dxf_entity的端点
    def getEndPoints(self):
        startp = []
        endp = []
        if self.dxf_entity.dxftype == 'LINE':
            startp = self.dxf_entity.start
            endp = self.dxf_entity.end
        elif self.dxf_entity.dxftype == 'ARC':
            startp = tuple(
                np.array(self.dxf_entity.center) + np.array([
                    np.cos(self.dxf_entity.start_angle),
                    np.sin(self.dxf_entity.start_angle)
                ]) * self.dxf_entity.radius)
            endp = tuple(
                np.array(self.dxf_entity.center) + np.array([
                    np.cos(self.dxf_entity.end_angle),
                    np.sin(self.dxf_entity.end_angle)
                ]) * self.dxf_entity.radius)
        return startp, endp

    # 根据dxfentity参数,计算entity的线段/弧线长度
    def getLength(self):
        length = 0
        if self.dxf_entity.dxftype == 'LINE':
            sp, ep = self.getEndPoints()
            length = gp.calcTwoPointsDistance(sp, ep)
            pass
        elif self.dxf_entity.dxftype == 'ARC':
            length = self.dxf_entity.radius * (
                self.dxf_entity.end_angle - self.dxf_entity.start_angle)
            pass
        else:
            pass
        return length

    # 根据dxf_entity参数,计算全部离散点GPS坐标
    def scatterGPSPoints(self):
        if self.dxf_entity.dxftype == 'LINE':
            sp, ep = self.getEndPoints()
            length = self.getLength()
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
        elif self.dxf_entity.dxftype == 'ARC':
            delta_angle = (
                self.dxf_entity.end_angle - self.dxf_entity.start_angle) / (
                    self.dxf_entity.radius * 2 * np.pi)  # 按照弧长为基准转换
            angle_list = np.arange(self.dxf_entity.start_angle,
                                   self.dxf_entity.end_angle, delta_angle)
            # points = np.array([np.cos(angle_list),
            #           np.sin(angle_list)
            #           ]) * self.dxf_entity.radius + self.dxf_entity.center
            xlist = np.cos(
                angle_list) * self.dxf_entity.radius + self.dxf_entity.center[0]
            ylist = np.sin(
                angle_list) * self.dxf_entity.radius + self.dxf_entity.center[1]
            points = tuple(zip(xlist, ylist))
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
        if self.dxf_entity.dxftype == 'ARC':
            self.dxf_entity.start_angle, self.dxf_entity.end_angle = self.dxf_entity.end_angle, self.dxf_entity.start_angle
            if self.dxf_entity.end_angle < self.dxf_entity.start_angle:
                self.dxf_entity.end_angle = self.dxf_entity.end_angle + 2 * np.pi
                print('changeEPTurn: angle:{}'.format(
                    (self.dxf_entity.start_angle, self.dxf_entity.end_angle)))
        elif self.dxf_entity.dxftype == 'LINE':
            self.dxf_entity.start, self.dxf_entity.end = self.dxf_entity.end, self.dxf_entity.start

    def isEqualtoLineEntity(self, line_entity):
        if self.dxf_entity.dxftype != line_entity.linetype:
            return False
        else:
            if line_entity.linetype == 'LINE':
                d0 = gp.calcTwoPointsDistance(self.dxf_entity.start,
                                              line_entity.start)
                d1 = gp.calcTwoPointsDistance(self.dxf_entity.end,
                                              line_entity.end)
                d2 = gp.calcTwoPointsDistance(self.dxf_entity.start,
                                              line_entity.end)
                d3 = gp.calcTwoPointsDistance(self.dxf_entity.end,
                                              line_entity.start)
                if (d0 == d2 and d1 == d3) or (d0 == d3 and d1 == d2):
                    return True
                else:
                    return False
            elif line_entity.linetype == 'ARC':
                dxf_center = np.array(self.dxf_entity.center)
                dxf_radius = np.array(self.dxf_entity.radius)
                d0 = gp.calcTwoPointsDistance(dxf_center, line_entity.center)
                if (d0 == 0) and ((
                    (dxf_radius - line_entity.radius) / dxf_radius) == 0):
                    return True
                else:
                    return False
                pass
            else:
                return False

    def getType(self):
        return self.dxf_entity.dxftype

    def getStart(self):
        return self.dxf_entity.start

    def getEnd(self):
        return self.dxf_entity.end

    def getCenter(self):
        return self.dxf_entity.center

    def getStartAngle(self):
        return self.dxf_entity.start_angle

    def getEndAngle(self):
        return self.dxf_entity.end_angle

    def getRadius(self):
        return self.dxf_entity.radius


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
    ax.set_xlim(-10, 1000)
    ax.set_ylim(-10, 1000)
    # ax.imshow(npimg1, origin='lower', zorder=0)
    ax.autoscale(False)

    # 读取dxf文件
    dxf_object = grb.readfile('../data/map/zhenjiang/zhenjiang.dxf')

    num = 0
    board_points = []
    for entity in dxf_object.entities:
        if entity.layer == 'ref_line':
            num = num + 1
            entity_in_map = EntityinMap(entity, scale, bias)
            line = entity_in_map.draw(color='r')
            ax.add_line(line)
        if entity.layer == 'board':
            entity_in_map = EntityinMap(entity, scale, bias)
            if entity_in_map.getType() == 'ARC':
                print('main: entity_in_map.center:{}'.format(
                    entity_in_map.dxf_entity.center))
            board_line = entity_in_map.draw(color='g')
            ax.add_line(board_line)
            points = entity_in_map.scatterGPSPoints()
            board_points.extend(points)
    board_points_tree = spt.KDTree(board_points)
    data = input('x, y = ')
    value = data.split(',')
    if len(value) == 2:
        point = [int(num) for num in value]
    else:
        point = [0, 0]

    width, points = gp.getWidthinP(point, 8 * scale, np.pi / 4,
                                   board_points_tree)
    print('width, points = {}, {}'.format(width, points))

    pline = ln.Line2D([points[0][0], points[1][0]],
                      [points[0][1], points[1][1]],
                      color='r')
    ax.add_line(pline)

    pline = ln.Line2D([point[0]], [point[1]], marker='o')
    ax.add_line(pline)
    near_points = board_points_tree.query_ball_point(point, 8 * scale)

    # print('points get {}'.format(board_points_tree.data[near_points]))
    for ind in near_points:
        value = board_points_tree.data[ind]
        pline = ln.Line2D([value[0]], [value[1]], marker='*', color='k')
        ax.add_line(pline)

    plt.show()
