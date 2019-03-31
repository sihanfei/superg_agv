# coding = utf-8

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as ln
import PIL.Image as PIImg
import dxfgrabber as grb
import copy as cp

import JsonFormat as jft
from line_entity import LineEntity
import scipy.spatial as spt
from gps_point import GPSPoint

total_step = 10


class EntityMapFig:
    """
    1.处理proc_line_entity_dict中的line_entities
    2.形成ref_line_dict
    3.将处理完成的entities存入done_line_entity_dict
    """

    def __init__(self, fig, entity_dict, scale):
        """
        从fig和entity_dict的差异上，判断哪些是已经处理完成的，哪些是尚带处理的
        """
        self.fig = fig
        self.ax = self.fig.gca()
        self.xlim_l, self.xlim_r = self.ax.get_xlim()
        self.ylim_l, self.ylim_r = self.ax.get_ylim()
        self.step = total_step
        self.xstep = (self.xlim_r - self.xlim_l) / (2 * self.step)
        self.ystep = (self.ylim_r - self.ylim_l) / (2 * self.step)
        self.total_line_entities_dict = entity_dict
        self.entity_dict = {}
        self.line2d_dict = {}
        for line in self.ax.lines:
            if line.get_picker() != 0 and line.get_url() != 'board':
                self.entity_dict[line.get_url()] = entity_dict[line.get_url()]
        self.scale = scale
        #
        self.board_artist = []
        #
        self.line_entity_id = 0
        self.entity = []
        self.artist = []
        self.start_point = []
        self.end_point = []
        self.start_point_line2d = []
        self.end_point_line2d = []
        self.done_line_entity_dict = {}  # 用来存储处理完成的line_entity
        #
        self.ref_line_dict = {}
        #
        self.mode = ''

    def setLineAsBoard(self, artist):
        return artist.get_xydata()

    def getNextRefLineID(self, current_ref_line_ID,
                         thres):  # 只有entity是新旧统一的，其他都不是，所以必须传递所有的entity
        current_PE = self.total_line_entities_dict[current_ref_line_ID].end
        print('currentPE={}, thres={}'.format(current_PE, thres))
        line_id = []
        for _, key in enumerate(self.total_line_entities_dict):
            if key != current_ref_line_ID:
                next_PS = self.total_line_entities_dict[key].start
                # next_PE = self.total_line_entities_dict[key].end
                dis0 = GPSPoint.calcTwoPointsDistance(current_PE, next_PS)
                # dis1 = GPSPoint.calcTwoPointsDistance(current_PE, next_PE)
                # print('nextPS={}, distance={}, nextPE={}, distance={}'.format(
                #     next_PS, dis0, next_PE, dis1))
                if dis0 <= thres:
                    line_id.append(key)
        print('line_id:{}'.format(line_id))
        return line_id

    def onPick(self, event):
        mousevent = event.mouseevent
        artist = event.artist
        if mousevent.button == 1:
            if self.mode == 'connect' and artist.get_url() != 'board':
                print(artist.get_url())
                line_id = self.getNextRefLineID(artist.get_url(),
                                                2 * self.scale)
                print('onPick: id:nextlist->{}:{}'.format(
                    artist.get_url(), line_id))
                artist.set_color('k')
                for id in line_id:
                    next_artist = self.line2d_dict[id]
                    next_artist.set_color['g']
                self.fig.canvas.draw()
            else:
                if artist.get_url() == 'board' and len(
                        self.start_point) != 0:  # 先选中车道线,再选边界
                    self.board_artist.append(artist)
                    artist.set_color('r')
                    artist.set_picker(0)
                    self.fig.canvas.draw()
                if self.line_entity_id == 0:
                    if artist.get_url() == 'board':
                        pass
                    else:
                        self.line_entity_id = int(artist.get_url())
                        self.entity = self.entity_dict[self.line_entity_id]
                        self.artist = artist
                        print('entity_map:xydata:{}'.format(
                            artist.get_xydata()))
                        self.artist.set_color('r')
                        self.ax.set_ylabel('line id = {}'.format(
                            self.line_entity_id))
                        self.fig.canvas.draw()
                else:
                    if artist == self.artist and len(self.start_point) == 0:
                        m_point = [mousevent.xdata, mousevent.ydata]
                        data = artist.get_xydata()
                        p0 = data[0]
                        p1 = data[-1]
                        print("onPick: p0={}, p1={}".format(p0, p1))
                        dis0 = GPSPoint.calcTwoPointsDistance(p0, m_point)
                        dis1 = GPSPoint.calcTwoPointsDistance(p1, m_point)
                        if dis0 <= dis1:
                            self.start_point = p0
                            self.end_point = p1
                        else:
                            self.start_point = p1
                            self.end_point = p0
                            print('start={}, end={}, angles={}'.format(
                                self.entity.start, self.entity.end,
                                self.entity.angles))
                            self.entity.changeEPTurn()  # 起点与entity是相反的
                            print('start={}, end={}, angles={}'.format(
                                self.entity.start, self.entity.end,
                                self.entity.angles))
                            # print(
                            # 'entity_map.py:onPick:{} is changeturn'.format(
                            # self.line_entity_id))
                        self.start_point_line2d = ln.Line2D(
                            [self.start_point[0]], [self.start_point[1]],
                            color='r',
                            marker='o')
                        self.end_point_line2d = ln.Line2D([self.end_point[0]],
                                                          [self.end_point[1]],
                                                          color='k',
                                                          marker='o')
                        self.ax.add_line(self.start_point_line2d)
                        self.ax.add_line(self.end_point_line2d)
                        self.artist.set_picker(0)
                        self.fig.canvas.draw()

    def onButtonPress(self, event):
        if event.button != 1:
            if len(self.start_point) > 0:
                self.start_point_line2d.set_color('b')
                self.start_point_line2d.set_marker(',')
                self.end_point_line2d.set_color('b')
                self.end_point_line2d.set_marker(',')
                self.end_point = []
                self.start_point = []
                # clear board
                for artist in self.board_artist:
                    artist.set_picker(5)
                    artist.set_color('g')
                self.board_artist.clear()
                self.artist.set_picker(5)
                self.fig.canvas.draw()
            else:
                if self.line_entity_id != 0:
                    self.artist.set_color('b')
                    self.line_entity_id = 0
                    self.artist = []
                    #
                    self.fig.canvas.draw()

    def OnMouseWheel(self, event):
        x_center = event.xdata
        y_center = event.ydata
        if event.button == 'up':
            if self.step > 0:
                self.step = self.step - 1
            if self.step != 0:
                self.ax.set_xlim(
                    max(x_center - self.step * self.xstep, self.xlim_l),
                    min(x_center + self.step * self.xstep, self.xlim_r))
                self.ax.set_ylim(
                    max(y_center - self.step * self.ystep, self.ylim_l),
                    min(y_center + self.step * self.ystep, self.ylim_r))
            else:
                self.ax.set_xlim(x_center - 10 * self.scale,
                                 x_center + 10 * self.scale)  # 这里会有问题
                self.ax.set_ylim(y_center - 10 * self.scale,
                                 y_center + 10 * self.scale)  # 先这么处理

        else:
            if self.step < total_step:
                self.step = self.step + 1
            if self.step != total_step:
                self.ax.set_xlim(
                    max(x_center - self.step * self.xstep, self.xlim_l),
                    min(x_center + self.step * self.xstep, self.xlim_r))
                self.ax.set_ylim(
                    max(y_center - self.step * self.ystep, self.ylim_l),
                    min(y_center + self.step * self.ystep, self.ylim_r))
            else:
                self.ax.set_xlim(self.xlim_l, self.xlim_r)
                self.ax.set_ylim(self.ylim_l, self.ylim_r)
            pass
        self.fig.canvas.draw()

    def releaseAllData(self):
        pass
        self.line_entity_id = 0
        self.start_point = []
        self.end_point = []
        self.artist = []
        for artist in self.board_artist:
            artist.set_picker(3)
            artist.set_color('g')
        self.board_artist.clear()

    def onKeyPress(self, event):
        if event.key == 'v':
            if len(self.entity_dict) - len(
                    self.done_line_entity_dict) == 0:  # 全部实体选择完成，开始连通图计算
                print('no entity_dict left')
                for line in self.ax.lines:  # turn on picker
                    if line.get_url() != 'board':
                        line.set_picker(3)
                        line.set_color('r')
                        self.line2d_dict[line.get_url()] = line
                self.mode = 'connect'
                self.fig.canvas.draw()
            if len(self.start_point) > 0 and len(
                    self.board_artist) > 0:  # 有中心线，也有边界
                board_data = []
                for artist in self.board_artist:
                    board_data.extend(artist.get_xydata())
                board_tree = spt.KDTree(board_data)
                print('entity_map: onKeyPress: sp, ep ={}'.format(
                    (self.start_point, self.end_point)))
                self.ref_line_dict[self.line_entity_id] = self.getRefLine(
                    self.entity, 8 * self.entity.scale, board_tree)  # 计算车道参考线
                self.done_line_entity_dict[self.line_entity_id] = self.entity
                left_entities_num = len(self.entity_dict) - len(
                    self.done_line_entity_dict)
                self.ax.set_xlabel('schedule : {}/{} entities'.format(
                    left_entities_num, len(self.entity_dict)))
                self.artist.set_color('k')
                self.artist.set_marker(',')
                self.releaseAllData()
                self.fig.canvas.draw()
            else:
                if len(self.done_line_entity_dict) > 0:
                    print("onKeyPress: no start point: total_len = {}".format(
                        len(self.done_line_entity_dict)))

        elif event.key == 'b':
            pass
        else:
            pass

    def callBackConnect(self):
        self.fig.canvas.mpl_connect('pick_event', self.onPick)
        self.fig.canvas.mpl_connect('button_press_event', self.onButtonPress)
        self.fig.canvas.mpl_connect('key_release_event', self.onKeyPress)
        self.fig.canvas.mpl_connect('scroll_event', self.OnMouseWheel)

    def callBackDisconnect(self):
        self.fig.canvas.mpl_disconnect(self.onPick)
        self.fig.canvas.mpl_disconnect(self.onButtonPress)
        self.fig.canvas.mpl_disconnect(self.onKeyPress)

    def getRefLine(self, line_entity, radius_thes, tree):
        points = line_entity.scatterGPSPoints()
        print('entity_map.py:points:{}'.format(points))
        ref_line = []
        if line_entity.linetype == 'LINE':
            for i in range(1, len(points)):
                ref_point = jft.RefPointPara()
                ref_point.point = points[i - 1]
                ref_point.theta = GPSPoint.getDiAngle(points[i - 1], points[i])
                ref_point.s = GPSPoint.calcTwoPointsDistance(
                    points[0], points[i - 1])
                ref_point.cuv = 0
                ref_point.gcuv = 0
                ref_point.width, _ = GPSPoint.getWidthinP(
                    points[i - 1], radius_thes, ref_point.theta, tree)
                # print('getRefLine: width:{}'.format(ref_point.width))
                ref_line.append(ref_point)
        elif line_entity.linetype == 'ARC':
            points_num = len(points)
            delta_angle = (
                line_entity.angles[1] - line_entity.angles[0]) / points_num
            angle_list = np.arange(line_entity.angles[0],
                                   line_entity.angles[1], delta_angle)
            for i in range(1, len(points)):
                ref_point = jft.RefPointPara()
                ref_point.point = points[i - 1]
                ref_point.theta = angle_list[i - 1] + delta_angle / np.abs(
                    delta_angle) * np.pi / 2  # 逆时针旋转,theta+90度
                ref_point.s = np.abs(angle_list[i - 1] - line_entity.angles[0]
                                     ) * line_entity.radius
                ref_point.cuv = 1 / line_entity.radius
                ref_point.gcuv = 0
                pass
                ref_point.width, _ = GPSPoint.getWidthinP(
                    points[i - 1], radius_thes, ref_point.theta, tree)
                # print('getRefLine: width:{}'.format(ref_point.width))
                ref_line.append(ref_point)
        print('entity_map.py: getRefLine: length of ref_line={}'.format(
            len(ref_line)))
        return ref_line


if __name__ == "__main__":
    file_dir = input('请输入数据文件所在地址与名称,如:../data/map/shenzhen/shenzhen:')
    if len(file_dir) == 0:
        file_dir = '../data/map/shenzhen/shenzhen'

    in_img_file = input('请输入图像文件名称,回车默认为:{}.bmp. [n]表示不需读入:'.format(file_dir))
    if len(in_img_file) == 0:
        in_img_file = file_dir + '.bmp'
    elif in_img_file == 'N' or in_img_file == 'n':
        in_img_file = False
    else:
        in_img_file = file_dir + in_img_file

    in_dxf_file = input('请输入DXF文件名称,回车默认为:{}.dxf:'.format(file_dir))
    if len(in_dxf_file) == 0:
        in_dxf_file = file_dir + '.dxf'
    else:
        in_dxf_file = file_dir + in_dxf_file

    inout_entities_map_file = input(
        '请输入line_entities地图文件名称,回车默认为:{}_line_entities_map.json'.format(
            file_dir))
    if len(inout_entities_map_file) == 0:
        inout_entities_map_file = file_dir + '_line_entities_map.json'
    else:
        inout_entities_map_file = file_dir + inout_entities_map_file

    # 准备绘图
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # 读入图像文件
    if in_img_file:
        img1 = PIImg.open(in_img_file)
        npimg1 = np.array(img1)
        npimg1 = npimg1[-1:0:-1, :, :]
        scale = 1.08
        bias = [0, 0]
        ax.imshow(npimg1, origin='lower')
        ax.autoscale(False)
    else:
        scale = 1
        bias = [0, 0]
        ax.set_xlim = (0, 1000)
        ax.set_ylim = (0, 1000)
        print('no img')

    # 读取json文件,保存的数据为line_entity,用于判断是否entity已经存在过,
    line_entities_json_file = inout_entities_map_file
    entities_map_obj = jft.readLineMapFromJson(line_entities_json_file)
    saved_line_entities_dict = {}
    if not entities_map_obj:
        print('main: entities_map.json not exist!')
    else:
        saved_line_entities_dict = jft.getLineEntryDictFromJsonObj(
            entities_map_obj)
    saved_entities_num = len(saved_line_entities_dict)
    saved_num_list = list(saved_line_entities_dict.keys())

    # 读取dxf文件
    dxf_object = grb.readfile(in_dxf_file)

    # 准备根据dxf文件进行绘图，仅仅把需要处理的entities传入map类中
    # connect_map因为需要整个地图，所以还是等退出后再计算
    # ref_line地图数据可以直接在绘图时生成，等退出后再存储
    num = 0  # 用于作为字典的key
    board_points = []  # 用于存放边界离散点
    total_line_entities_dict = {}  # 需要处理的line_entities
    # 查找所有dxf_entities
    for entity in dxf_object.entities:
        if entity.layer == 'ref_line':
            num = num + 1
            entity_in_map = LineEntity()
            entity_in_map.initFromDXF(entity, scale, bias)  #
            # 先简单考虑:对于同一个dxf文件,entities的顺序是确定的,因此可以直接通过num(也就是ID)来比对
            if num in saved_num_list:
                line = entity_in_map.draw(color='k', picker=0, url=num)
                # procing_line_entities_dict[
                #     num] = entity_in_map  # 传递的是line_entity,为了统计全部的entities,先把数据传进去
            else:
                line = entity_in_map.draw(color='b', picker=5, url=num)
            total_line_entities_dict[num] = entity_in_map
            ax.add_line(line)

        if entity.layer == 'board':
            entity_in_map = LineEntity()
            entity_in_map.initFromDXF(entity, scale, bias)  #
            # if entity_in_map.getType() == 'ARC':
            #     print('main: entity_in_map.center:{}'.format(
            #         entity_in_map.dxf_entity.center))
            board_line = entity_in_map.draw(color='g', url='board', picker='5')
            ax.add_line(board_line)
            points = entity_in_map.scatterGPSPoints()
            board_points.extend(points)

    ax.set_xlabel('{}/{} entities'.format(
        len(total_line_entities_dict) - saved_entities_num, num))
    ax.set_title('1.select_ref 2.select_start 3.select_board 4."v" to save')

    # 调用EntityMapFig
    zhenjiang_map = EntityMapFig(fig, total_line_entities_dict, scale)
    zhenjiang_map.callBackConnect()
    plt.show()
    zhenjiang_map.callBackDisconnect()
