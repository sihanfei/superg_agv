# coding = utf-8

# 根据dxf生成连通地图和参考线
# 根据dxf的entity生成参考线图

# 根据选择的起点,对entity的起终点进行重新排序,假定entity本身的排列是有序的,并对entity的起终点进行去重
# 选择entity: black
# 按b后,选择起点: red, 标注起点p, 如果点击鼠标右键,重新选择起点；如果无起点,退回entity选择
# 按r后,描绘ref_lin: red,标注起点和终点
# 按v后,保存数据:white

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.lines as ln
import PIL.Image as PIImg
import dxfgrabber as grb

import JsonFormat as jft


class ModifyMap:
    def __init__(self, fig, entity_dict):
        self.fig = fig
        self.ax = self.fig.gca()
        self.entity_dict = entity_dict
        #
        self.line_entity_dict = {}
        self.line_entity_id = 0
        self.entity = []
        self.artist = []
        self.start_point = []
        self.end_point = []
        self.start_point_line2d = []
        self.end_point_line2d = []

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
            else:
                if artist == self.artist and len(self.start_point) == 0:
                    m_point = [mousevent.xdata, mousevent.ydata]
                    data = artist.get_xydata()
                    p0 = data[0]
                    p1 = data[-1]
                    print("onPick: p0={}, p1={}".format(p0, p1))
                    dis0 = self.calcDistance(p0, m_point)
                    dis1 = self.calcDistance(p1, m_point)
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

    def calcDistance(self, p1, p2):
        distance = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        return distance

    def drawPoint(self, point, color):
        # print('draw_point is {}'.format(point))
        plt.plot(point[0], point[1], color)

    def onButtonPress(self, event):
        if event.button != 1:
            if len(self.start_point) > 0:
                self.start_point_line2d.set_color('b')
                self.start_point_line2d.set_marker('.')
                self.end_point_line2d.set_color('b')
                self.end_point_line2d.set_marker('.')
                self.end_point = []
                self.start_point = []
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
                jft.saveLineMapToJson('Line_Map.json', 'w',
                                      self.line_entity_dict)
                self.artist.set_color('w')
                self.artist.set_marker('>')
                self.releaseAllData()
                self.fig.canvas.draw()
                pass
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


"""##############################################
"""
if __name__ == "__main__":
    img1 = PIImg.open("zhenjiang.bmp")
    npimg1 = np.array(img1)
    npimg1 = npimg1[-1:0:-1, :, :]
    scale = 1 / 0.116
    bias = [18.75, -0.75]
    # xyz_map = (xyz_map - bias) * scale  # 针对镇江地图的偏移

    # 准备绘图
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title("'v' save json")

    # 读取dxf文件
    dxf_object = grb.readfile('map7.dxf')

    total_ref_seg_id_list = []
    total_ref_seg_entity = []
    total_ref_seg_dict = {}
    ref_seg_id = 0

    for entity in dxf_object.entities:
        if entity.layer == 'ref_line':
            ref_seg_id = ref_seg_id + 1
            if entity.dxftype == 'LINE':  # 对点进行离散化
                entity.start = (np.array(entity.start) / 1000 - bias) * scale
                entity.end = (np.array(entity.end) / 1000 - bias) * scale
                start_point = entity.start
                end_point = entity.end
                # x = (np.array([start_point[0], end_point[0]])/1000 - bias[0]) * scale
                # y = (np.array([start_point[1], end_point[1]])/1000 - bias[1]) * scale
                x = np.array([start_point[0], end_point[0]])
                y = np.array([start_point[1], end_point[1]])
                # # print('x={}'.format(x))
                # 利用line的url属性传递entity的id信息
                aline = ln.Line2D(
                    x, y, url=str(ref_seg_id), picker=3, color='b')
                ax.add_line(aline)
            if entity.dxftype == 'ARC':
                entity.center = (
                    np.array(entity.center) / 1000.0 - bias) * scale
                center_point = entity.center

                entity.radius = entity.radius / 1000.0 * scale
                radius = entity.radius

                entity.start_angle = entity.start_angle * np.pi / 180
                start_angle = entity.start_angle

                if entity.end_angle == 0:
                    entity.end_angle = 2 * np.pi
                else:
                    entity.end_angle = entity.end_angle * np.pi / 180
                end_angle = entity.end_angle

                delta_angle = (end_angle - start_angle) / (radius * 2 * np.pi
                                                           )  # 按照弧长为基准转换
                angle_array = np.arange(start_angle, end_angle, delta_angle)

                x = (np.cos(angle_array) * radius + center_point[0])
                y = (np.sin(angle_array) * radius + center_point[1])

                aline = ln.Line2D(
                    x, y, url=str(ref_seg_id), picker=3, color='b')
                ax.add_line(aline)

            total_ref_seg_dict[ref_seg_id] = entity

    # 显示并关联到选点程序
    ax.imshow(npimg1, origin='lower')
    ax.autoscale(False)
    map_modi = ModifyMap(fig, total_ref_seg_dict)
    map_modi.callBackConnect()
    plt.show()
