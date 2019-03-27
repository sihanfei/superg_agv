# coding = utf-8

import numpy as np
from gps_point import GPSPoint as gp
import JsonFormat as jft
import matplotlib.pyplot as plt
import matplotlib.lines as ln
import PIL.Image as PIImg
import dxfgrabber as grb
import copy as cp
import dxf_entity
import scipy.spatial as spt


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

    def getRefLine(self, entity):

        return


if __name__ == "__main__":
    in_img_file = input('请输入图像文件名称,回车默认为:../data/map/zhenjiang/zhenjiang.bmp')
    if len(in_img_file) == 0:
        in_img_file = '../data/map/zhenjiang/zhenjiang.bmp'

    in_dxf_file = input('请输入DXF文件名称,回车默认为:../data/map/zhenjiang/zhenjiang.dxf')
    if len(in_dxf_file) == 0:
        in_dxf_file = '../data/map/zhenjiang/zhenjiang.dxf'

    inout_entities_map_file = input(
        '请输入地图文件名称,回车默认为:../data/map/zhenjiang/entities_map.json')
    if len(inout_entities_map_file) == 0:
        inout_entities_map_file = '../data/map/zhenjiang/entities_map.json'

    out_connect_map_file = input(
        '请输入有向连通地图文件名称,回车默认为:../data/map/zhenjiang/connect_map.json')
    if len(out_connect_map_file) == 0:
        out_connect_map_file = '../data/map/zhenjiang/connect_map.json'

    out_ref_line_map_file = input(
        '请输入参考线地图文件名称,回车默认为:../data/map/zhenjiang/ref_line_map.json')
    if len(out_ref_line_map_file) == 0:
        out_ref_line_map_file = '../data/map/zhenjiang/ref_line_map.json'

    # 读入图像文件
    img1 = PIImg.open(in_img_file)
    npimg1 = np.array(img1)
    npimg1 = npimg1[-1:0:-1, :, :]
    scale = 1 / 0.116
    bias = [-18.75, +0.75]

    # 准备绘图
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # 读取json文件,保存的数据为line_entity,用于判断是否entity已经存在过,
    line_entities_json_file = inout_entities_map_file
    entities_map_obj = jft.readLineMapFromJson(line_entities_json_file)
    if not entities_map_obj:
        print('main: entities_map.json not exist!')
    else:
        saved_line_entities_dict = jft.getLineEntryDictFromJsonObj(
            entities_map_obj)

    # 读取dxf文件
    dxf_object = grb.readfile(in_dxf_file)

    # 准备根据dxf文件进行绘图，仅仅把需要处理的entities传入map类中
    # connect_map因为需要整个地图，所以还是等退出后再计算
    # ref_line地图数据可以直接在绘图时生成，等退出后再存储
    num = 0  # 用于作为字典的key
    board_points = []  # 用于存放边界离散点
    procing_line_entities_dict = {}
    for entity in dxf_object.entities:
        if entity.layer == 'ref_line':
            num = num + 1
            entity_in_map = dxf_entity.EntityinMap(entity, scale, bias)
            # 先简单考虑:对于同一个dxf文件,entities的顺序是确定的,因此可以直接通过num(也就是ID)来比对
            if len(saved_line_entities_dict) != 0:
                if entity_in_map.isEqualtoLineEntity(
                        saved_line_entities_dict[num]):
                    line = entity_in_map.draw(color='w', picker=0)
                else:
                    line = entity_in_map.draw(color='k', picker=5)
                    procing_line_entities_dict[num] = entity_in_map.dxf_entity
            else:
                line = entity_in_map.draw(color='k', picker=5)
                procing_line_entities_dict[num] = entity_in_map.toLineEntity()

            ax.add_line(line)

        if entity.layer == 'board':
            entity_in_map = dxf_entity.EntityinMap(entity, scale, bias)
            if entity_in_map.getType() == 'ARC':
                print('main: entity_in_map.center:{}'.format(
                    entity_in_map.dxf_entity.center))
            board_line = entity_in_map.draw(color='k')
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
    pline = ln.Line2D([point[0]], [point[1]], marker='o')
    ax.add_line(pline)
    near_points = board_points_tree.query_ball_point(point, 8 * scale)
    print('points get {}'.format(near_points))
    for ind in near_points:
        value = board_points_tree.data[ind]
        pline = ln.Line2D([value[0]], [value[1]], marker='*', color='k')
        ax.add_line(pline)
    plt.show()
