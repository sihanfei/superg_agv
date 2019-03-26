# coding = utf-8

import numpy as np
from gps_point import GPSPoint as gp
import JsonFormat as jft
import matplotlib.pyplot as plt
import matplotlib.lines as ln
import PIL.Image as PIImg
import dxfgrabber as grb
import copy as cp
import dxf_entity as dent


class EntityMapFig:
    def __init__(self, fig, entity_dict):
        self.fig = fig
        self.ax = self.fig.gca()
        self.entity_dict = entity_dict
        #
        self.line_entity_id = 0
        self.entity = []
        self.artist = []
        self.start_point = []
        self.end_point = []
        self.start_point_line2d = []
        self.end_point_line2d = []
        self.line_entity_dict = {}

    def onPick(self, event):
        mousevent = event.mouseevent
        artist = event.artist
        if mousevent.button == 1:
            if self.line_entity_id == 0:
                self.line_entity_id = int(artist.get_url())
                self.entity = self.entity_dict[self.line_entity_id]
                self.artist = artist
                self.artist.set_color('r')
                self.fig.canvas.draw()
                print("onPick: id={}".format(self.line_entity_id))
                if self.entity.dxftype == 'ARC':
                    print("onPick: id={}, sangle={}, eangle={}".format(
                        self.line_entity_id, self.entity.start_angle,
                        self.entity.end_angle))
            else:
                if artist == self.artist and len(self.start_point) == 0:
                    m_point = [mousevent.xdata, mousevent.ydata]
                    data = artist.get_xydata()
                    p0 = data[0]
                    p1 = data[-1]
                    print("onPick: p0={}, p1={}".format(p0, p1))
                    dis0 = gp.calcTwoPointsDistance(p0, m_point)
                    dis1 = gp.calcTwoPointsDistance(p1, m_point)
                    if dis0 <= dis1:
                        self.start_point = p0
                        self.end_point = p1
                    else:
                        self.start_point = p1
                        self.end_point = p0
                    self.start_point_line2d = ln.Line2D(
                        [self.start_point[0], self.start_point[0]],
                        [self.start_point[1], self.start_point[1]],
                        color='r',
                        marker='o')
                    self.end_point_line2d = ln.Line2D(
                        [self.end_point[0], self.end_point[0]],
                        [self.end_point[1], self.end_point[1]],
                        color='k',
                        marker='o')
                    self.ax.add_line(self.start_point_line2d)
                    self.ax.add_line(self.end_point_line2d)
                    self.fig.canvas.draw()
        # # print('draw list len = {}, artist len = {}'.format(len(self.draw_entity_list), len(self.draw_artist_list)))

    def onButtonPress(self, event):
        if event.button != 1:
            if len(self.start_point) > 0:
                self.start_point_line2d.set_color('b')
                self.start_point_line2d.set_marker(',')
                self.end_point_line2d.set_color('b')
                self.end_point_line2d.set_marker(',')
                self.end_point = []
                self.start_point = []
                self.fig.canvas.draw()
            else:
                if self.line_entity_id != 0:
                    self.artist.set_color('b')
                    self.line_entity_id = 0
                    self.artist = []
                    self.fig.canvas.draw()

    def releaseAllData(self):
        pass
        self.line_entity_id = 0
        self.start_point = []
        self.end_point = []
        self.artist = []

    def onKeyPress(self, event):
        if event.key == 'v':
            if len(self.start_point) > 0:
                line_type = self.entity.dxftype
                if line_type == 'ARC':
                    value = jft.LineEntity(
                        line_type, self.start_point, self.end_point,
                        [self.entity.start_angle, self.entity.end_angle],
                        self.entity.center, self.entity.radius)
                elif line_type == 'LINE':
                    value = jft.LineEntity(line_type, self.start_point,
                                           self.end_point, [0.0, 0.0],
                                           [0.0, 0.0], 0)
                else:
                    value = jft.LineEntity()
                self.line_entity_dict[self.line_entity_id] = value
                print("onKeyPress: line_entity: {} : {}".format(
                    self.line_entity_id, value.linetype))
                self.artist.set_color('w')
                self.artist.set_marker('.')
                self.releaseAllData()
                self.fig.canvas.draw()
                pass
            else:
                if len(self.line_entity_dict) > 0:
                    print("onKeyPress: no start point: total_len = {}".format(
                        len(self.line_entity_dict)))

        elif event.key == 'b':
            pass
        else:
            pass

    def callBackConnect(self):
        self.fig.canvas.mpl_connect('pick_event', self.onPick)
        self.fig.canvas.mpl_connect('button_press_event', self.onButtonPress)
        self.fig.canvas.mpl_connect('key_release_event', self.onKeyPress)

    def callBackDisconnect(self):
        self.fig.canvas.mpl_disconnect(self.onPick)
        self.fig.canvas.mpl_disconnect(self.onButtonPress)
        self.fig.canvas.mpl_disconnect(self.onKeyPress)


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
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    # ax.imshow(npimg1, origin='lower', zorder=0)
    ax.autoscale(False)

    # 读取dxf_entities_dict.json
    # saved_entities_dict = jft.readLineMapFromJson()

    # 读取dxf文件
    dxf_object = grb.readfile('../data/map/zhenjiang/zhenjiang.dxf')

    num = 0
    for entity in dxf_object.entities:
        if entity.layer == 'ref_line':
            num = num + 1
            entity_in_map = dent.EntityinMap(entity, scale, bias)
            # 判断是否已经在dxf_entities_dict.json中存在,如果存在,设置颜色为白色,picker=0
            line = entity_in_map.draw(color='r')
            ax.add_line(line)
    print('total entities is {}'.format(num))
    plt.show()

    # 合并两个字典
    # new_entities_dict = dict(saved_entities_dict, **new_entities_dict)
    # 保存文件
