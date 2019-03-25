# coding = utf-8

# figure artist -> url -> entityID -> entity -> x,y,type
#    ^                                            |
#    |____________________________________________|

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
import map_interface as mif


def calcDistance(p1, p2):
    distance = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    return distance


def drawPoint(point, color):
    # print('draw_point is {}'.format(point))
    plt.plot(point[0], point[1], color)


class ModifyMap:
    def __init__(self, fig, entity_dict, line_entity_dict, filename):
        self.filename = filename
        self.fig = fig
        self.ax = self.fig.gca()
        self.entity_dict = entity_dict
        #
        self.line_entity_dict = line_entity_dict
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
                    dis0 = calcDistance(p0, m_point)
                    dis1 = calcDistance(p1, m_point)
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
                jft.saveLineMapToJson(self.filename, 'w',
                                      self.line_entity_dict)
                self.artist.set_color('w')
                self.artist.set_marker('.')
                self.releaseAllData()
                self.fig.canvas.draw()
                pass
            else:
                if len(self.line_entity_dict) > 0:
                    print("onKeyPress: no start point: total_len = {}".format(
                        len(self.line_entity_dict)))
                    jft.saveLineMapToJson(self.filename, 'w',
                                          self.line_entity_dict)

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


class EntityProc():
    def testEntityEqual(self, dxf_entity, line_entity, bias, scale):
        if dxf_entity.dxftype == line_entity.linetype:
            if dxf_entity.dxftype == "LINE":
                dxf_start = (np.array(dxf_entity.start) / 1000 - bias) * scale
                dxf_end = (np.array(dxf_entity.end) / 1000 - bias) * scale
                d0 = calcDistance(dxf_start, line_entity.start)
                d1 = calcDistance(dxf_end, line_entity.end)
                d2 = calcDistance(dxf_start, line_entity.end)
                d3 = calcDistance(dxf_end, line_entity.start)
                if (d0 == 0 and d1 == 0) or (d2 == 0 and d3 == 0):
                    # print('EntityProc: dxf_start:{}, dxf_end:{}'.format(
                    #     dxf_start, dxf_end))
                    return True
                else:
                    return False
            elif dxf_entity.dxftype == "ARC":
                dxf_center = (
                    np.array(dxf_entity.center) / 1000 - bias) * scale
                dxf_radius = np.array(dxf_entity.radius) / 1000 * scale
                d0 = calcDistance(dxf_center, line_entity.center)
                if (d0 == 0) and ((
                    (dxf_radius - line_entity.radius) / dxf_radius) == 0):
                    # print('EntityProc: dxf_center:{}, dxf_radius:{}'.format(
                    #     dxf_center, dxf_radius))
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False


def combineShowImgAndDXF(img_file, dxf_file):
    pass


def buildMapFromDXF(in_img_file, in_dxf_file, inout_entities_map_file,
                    out_connect_map_file, out_ref_line_map_file):
    img1 = PIImg.open(in_img_file)
    npimg1 = np.array(img1)
    npimg1 = npimg1[-1:0:-1, :, :]
    scale = 1 / 0.116
    bias = [18.75, -0.75]
    # xyz_map = (xyz_map - bias) * scale  # 针对镇江地图的偏移

    # 准备绘图
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # 读取dxf文件
    dxf_object = grb.readfile(in_dxf_file)

    total_ref_seg_dict = {}
    ref_seg_id = 0

    # 读取json文件,看是否entity已经存在过,
    line_entities_json_file = inout_entities_map_file
    entities_map_obj = jft.readLineMapFromJson(line_entities_json_file)
    line_entities_dict = {}
    drawn_entities_num = 0
    if not entities_map_obj:
        print('main: entities_map.json not exist!')
    else:
        entity_proc = EntityProc()
        line_entities_dict = jft.getLineEntryDictFromJsonObj(entities_map_obj)
        for _, key in enumerate(line_entities_dict):
            line_entity = line_entities_dict[key]
            print('main: getLineEntryDictFromJsonObj->{}:{}'.format(
                key, line_entity.start))
        pass
    # 如果存在过, 则将相应的entity标注为已经选中,即将picker设置为0,颜色为白色
    for entity in dxf_object.entities:
        if entity.layer == 'ref_line':
            ref_seg_id = ref_seg_id + 1
            exist = False
            line_entities_dict_key = []
            if len(line_entities_dict) != 0:  # 判断entity是否已经存在了,
                for _, key in enumerate(line_entities_dict):
                    exist = entity_proc.testEntityEqual(
                        entity, line_entities_dict[key], bias,
                        scale)  # testEntityEqual有一定的问题,在arc的判断上
                    if exist:
                        drawn_entities_num = drawn_entities_num + 1
                        line_entities_dict_key = key
                        break
            if exist:
                print('main: get a entity -> {}'.format(ref_seg_id))
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
                    x, y, url=str(ref_seg_id), picker=5, color='b', marker=',')
                if exist:
                    aline.set_color('w')
                    aline.set_picker(0)
                    drawPoint(line_entities_dict[line_entities_dict_key].start,
                              'ro')
                    drawPoint(line_entities_dict[line_entities_dict_key].end,
                              'ko')
                    print('main: get a entity line <--')
                ax.add_line(aline)

            if entity.dxftype == 'ARC':
                entity.center = (
                    np.array(entity.center) / 1000.0 - bias) * scale
                center_point = entity.center

                entity.radius = entity.radius / 1000.0 * scale
                radius = entity.radius

                entity.start_angle = entity.start_angle * np.pi / 180
                entity.end_angle = entity.end_angle * np.pi / 180
                if entity.start_angle > entity.end_angle:
                    entity.start_angle = entity.start_angle - 2 * np.pi
                start_angle = entity.start_angle
                end_angle = entity.end_angle

                delta_angle = (end_angle - start_angle) / (radius * 2 * np.pi
                                                           )  # 按照弧长为基准转换
                angle_array = np.arange(start_angle, end_angle, delta_angle)

                x = (np.cos(angle_array) * radius + center_point[0])
                y = (np.sin(angle_array) * radius + center_point[1])

                aline = ln.Line2D(
                    x, y, url=str(ref_seg_id), picker=5, color='b', marker=',')
                if exist:
                    aline.set_color('w')
                    aline.set_picker(0)
                    drawPoint(line_entities_dict[line_entities_dict_key].start,
                              'ro')
                    drawPoint(line_entities_dict[line_entities_dict_key].end,
                              'ko')
                    print('main: get a entity arc <--')
                ax.add_line(aline)
            # save to dict
            total_ref_seg_dict[ref_seg_id] = entity
    left_entities = ref_seg_id - drawn_entities_num  # 剩余还未处理的实体数量
    # 显示并关联到选点程序
    ax.set_title("1.pick a line.  2.pick start point.    3.'v' save json")
    ax.set_xlabel(str(left_entities) + ' Entities left')
    ax.imshow(npimg1, origin='lower')
    ax.autoscale(False)
    map_modi = ModifyMap(fig, total_ref_seg_dict, line_entities_dict,
                         line_entities_json_file)
    map_modi.callBackConnect()
    plt.show()

    # 计算离散点\
    entities_map_obj = jft.readLineMapFromJson(line_entities_json_file)
    entities_dict = {}
    # read data from file
    if not entities_map_obj:
        print('main: file not exist!')
    else:
        for _, key in enumerate(entities_map_obj):
            if key == 0:
                print("main: {}:{}".format(key, entities_map_obj[key][0]))
            entity = jft.LineEntity(
                entities_map_obj[key][0], entities_map_obj[key][1],
                entities_map_obj[key][2], entities_map_obj[key][3],
                entities_map_obj[key][4], entities_map_obj[key][5])
            entities_dict[key] = entity
        # connectmap
        calc_ref_line = mif.CalcRefLine()
        connect_map_dict = calc_ref_line.makeConnectMap(entities_dict, 2)
        # 保存连通图数据
        fp = open(out_connect_map_file, 'w')
        for _, key in enumerate(connect_map_dict):
            value = connect_map_dict[key]
            number = len(value)
            fp.write(key)
            fp.write(',')
            fp.write(str(number))
            for id in value:
                fp.write(',')
                fp.write(id)
            fp.write('\n')
        fp.close()
        # ref_line
        ref_line_dict = {}
        for _, key in enumerate(entities_dict):
            entity = entities_dict[key]
            ref_line = calc_ref_line.getRefLine(entity)
            ref_line_dict[key] = ref_line
        # 保存参考点数据
        #  point=[0.0, 0.0],
        #  width=[2, 2],
        #  cuv=0,
        #  gcuv=0,
        #  s=0,
        #  theta=0):
        fp = open(out_ref_line_map_file, 'w')
        for _, key in enumerate(ref_line_dict):
            ref_line = ref_line_dict[key]
            for data in ref_line:
                fp.write(key)
                fp.write(',')
                fp.write(str(data.point[0]))
                fp.write(',')
                fp.write(str(data.point[1]))
                fp.write(',')
                fp.write(str(data.s))
                fp.write(',')
                fp.write(str(data.theta))
                fp.write(',')
                fp.write(str(data.cuv))
                fp.write(',')
                fp.write(str(data.gcuv))
                fp.write(',')
                fp.write(str(data.width[0]))
                fp.write(',')
                fp.write(str(data.width[1]))
                fp.write('\n')
        fp.close()


"""##############################################
"""
if __name__ == "__main__":
    # buildMapFromDXF('../data/map/zhenjiang/zhenjiang.bmp',
    #                 '../data/map/zhenjiang/zhenjiang.dxf',
    #                 '../data/map/zhenjiang/entities_map.json',
    #                 '../data/map/zhenjiang/connect_map.json',
    #                 '../data/map/zhenjiang/ref_line_map.json')

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

    img1 = PIImg.open(in_img_file)
    npimg1 = np.array(img1)
    npimg1 = npimg1[-1:0:-1, :, :]
    scale = 1 / 0.116
    bias = [18.75, -0.75]
    # xyz_map = (xyz_map - bias) * scale  # 针对镇江地图的偏移

    # 准备绘图
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # 读取dxf文件
    dxf_object = grb.readfile(in_dxf_file)

    total_ref_seg_dict = {}
    ref_seg_id = 0

    # 读取json文件,看是否entity已经存在过,
    line_entities_json_file = inout_entities_map_file
    entities_map_obj = jft.readLineMapFromJson(line_entities_json_file)
    line_entities_dict = {}
    drawn_entities_num = 0
    if not entities_map_obj:
        print('main: entities_map.json not exist!')
    else:
        entity_proc = EntityProc()
        line_entities_dict = jft.getLineEntryDictFromJsonObj(entities_map_obj)
        for _, key in enumerate(line_entities_dict):
            line_entity = line_entities_dict[key]
            print('main: getLineEntryDictFromJsonObj->{}:{}'.format(
                key, line_entity.start))
        pass
    # 如果存在过, 则将相应的entity标注为已经选中,即将picker设置为0,颜色为白色
    for entity in dxf_object.entities:
        if entity.layer == 'ref_line':
            ref_seg_id = ref_seg_id + 1
            exist = False
            line_entities_dict_key = []
            if len(line_entities_dict) != 0:  # 判断entity是否已经存在了,
                for _, key in enumerate(line_entities_dict):
                    exist = entity_proc.testEntityEqual(
                        entity, line_entities_dict[key], bias,
                        scale)  # testEntityEqual有一定的问题,在arc的判断上
                    if exist:
                        drawn_entities_num = drawn_entities_num + 1
                        line_entities_dict_key = key
                        break
            if exist:
                print('main: get a entity -> {}'.format(ref_seg_id))
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
                    x, y, url=str(ref_seg_id), picker=5, color='b', marker=',')
                if exist:
                    aline.set_color('w')
                    aline.set_picker(0)
                    drawPoint(line_entities_dict[line_entities_dict_key].start,
                              'ro')
                    drawPoint(line_entities_dict[line_entities_dict_key].end,
                              'ko')
                    print('main: get a entity line <--')
                ax.add_line(aline)

            if entity.dxftype == 'ARC':
                entity.center = (
                    np.array(entity.center) / 1000.0 - bias) * scale
                center_point = entity.center

                entity.radius = entity.radius / 1000.0 * scale
                radius = entity.radius

                entity.start_angle = entity.start_angle * np.pi / 180
                entity.end_angle = entity.end_angle * np.pi / 180
                if entity.start_angle > entity.end_angle:
                    entity.start_angle = entity.start_angle - 2 * np.pi
                start_angle = entity.start_angle
                end_angle = entity.end_angle

                delta_angle = (end_angle - start_angle) / (radius * 2 * np.pi
                                                           )  # 按照弧长为基准转换
                angle_array = np.arange(start_angle, end_angle, delta_angle)

                x = (np.cos(angle_array) * radius + center_point[0])
                y = (np.sin(angle_array) * radius + center_point[1])

                aline = ln.Line2D(
                    x, y, url=str(ref_seg_id), picker=5, color='b', marker=',')
                if exist:
                    aline.set_color('w')
                    aline.set_picker(0)
                    drawPoint(line_entities_dict[line_entities_dict_key].start,
                              'ro')
                    drawPoint(line_entities_dict[line_entities_dict_key].end,
                              'ko')
                    print('main: get a entity arc <--')
                ax.add_line(aline)
            # save to dict
            total_ref_seg_dict[ref_seg_id] = entity
    left_entities = ref_seg_id - drawn_entities_num  # 剩余还未处理的实体数量
    # 显示并关联到选点程序
    ax.set_title("1.pick a line.  2.pick start point.    3.'v' save json")
    ax.set_xlabel(str(left_entities) + ' Entities left')
    ax.imshow(npimg1, origin='lower')
    ax.autoscale(False)
    map_modi = ModifyMap(fig, total_ref_seg_dict, line_entities_dict,
                         line_entities_json_file)
    map_modi.callBackConnect()
    plt.show()

    # 计算离散点\
    entities_map_obj = jft.readLineMapFromJson(line_entities_json_file)
    entities_dict = {}
    # read data from file
    if not entities_map_obj:
        print('main: file not exist!')
    else:
        for _, key in enumerate(entities_map_obj):
            if key == 0:
                print("main: {}:{}".format(key, entities_map_obj[key][0]))
            entity = jft.LineEntity(
                entities_map_obj[key][0], entities_map_obj[key][1],
                entities_map_obj[key][2], entities_map_obj[key][3],
                entities_map_obj[key][4], entities_map_obj[key][5])
            entities_dict[key] = entity
        # connectmap
        calc_ref_line = mif.CalcRefLine()
        connect_map_dict = calc_ref_line.makeConnectMap(entities_dict, 2)
        # 保存连通图数据
        fp = open(out_connect_map_file, 'w')
        for _, key in enumerate(connect_map_dict):
            value = connect_map_dict[key]
            number = len(value)
            fp.write(key)
            fp.write(',')
            fp.write(str(number))
            for id in value:
                fp.write(',')
                fp.write(id)
            fp.write('\n')
        fp.close()
        # ref_line
        ref_line_dict = {}
        for _, key in enumerate(entities_dict):
            entity = entities_dict[key]
            ref_line = calc_ref_line.getRefLine(entity)
            ref_line_dict[key] = ref_line
        # 保存参考点数据
        #  point=[0.0, 0.0],
        #  width=[2, 2],
        #  cuv=0,
        #  gcuv=0,
        #  s=0,
        #  theta=0):
        fp = open(out_ref_line_map_file, 'w')
        for _, key in enumerate(ref_line_dict):
            ref_line = ref_line_dict[key]
            for data in ref_line:
                fp.write(key)
                fp.write(',')
                fp.write(str(data.point[0]))
                fp.write(',')
                fp.write(str(data.point[1]))
                fp.write(',')
                fp.write(str(data.s))
                fp.write(',')
                fp.write(str(data.theta))
                fp.write(',')
                fp.write(str(data.cuv))
                fp.write(',')
                fp.write(str(data.gcuv))
                fp.write(',')
                fp.write(str(data.width[0]))
                fp.write(',')
                fp.write(str(data.width[1]))
                fp.write('\n')
        fp.close()
