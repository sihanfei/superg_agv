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
import scipy.spatial as spt

import JsonFormat as jft
from gps_point import GPSPoint
from line_entity import LineEntity
from entity_map import EntityMapFig

import csv


def getConnectMap(entities_dict, threshold):
    # currentEntityID : (nextID0, ..., nextIDn)
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
            distance = GPSPoint.calcTwoPointsDistance(endp, startp)
            if distance < threshold:
                connect_value_list.append(keyS)
        connect_map_dict[keyE] = connect_value_list
        print("makConnectMap: connect_dict={}:{}".format(
            keyE, connect_value_list))
    return connect_map_dict


def saveRefLineToFile(out_ref_line_map_file, ref_line_dict, wt):
    fp = open(out_ref_line_map_file, wt)
    for _, key in enumerate(ref_line_dict):
        ref_line = ref_line_dict[key]
        for data in ref_line:
            fp.write(str(key))
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


def saveConnectMapTofile(out_connect_map_file, connect_map_dict):
    # 保存连通图数据
    fp = open(out_connect_map_file, 'w+')
    for _, key in enumerate(connect_map_dict):
        value = connect_map_dict[key]
        number = len(value)
        fp.write(str(key))
        fp.write(',')
        fp.write(str(number))
        for id in value:
            fp.write(',')
            fp.write(str(id))
        fp.write('\n')
    fp.close()


if __name__ == "__main__":
    file_dir = input('请输入数据文件所在地址与名称,如:./data/shenzhen/shenzhen:')
    if len(file_dir) == 0:
        file_dir = './data/shenzhen/shenzhen'

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
        scale = float(input('input the scale: '))
        bias_str = input('input the bias by ",": ')
        bias_list = bias_str.split(',')
        bias = [float(bias_list[0]), float(bias_list[1])]
        ax.imshow(npimg1, origin='lower')
        # ax.autoscale(False)
        ax.autoscale(True)
        ax.set_xlim(-100, 1000)
        ax.set_ylim(-100, 1000)
    else:
        scale = 1
        bias = [0, 0]
        print('no img')
        ax.set_xlim = [-100, 1000]
        ax.set_ylim = [-100, 1000]
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
                line = saved_line_entities_dict[num].draw(
                    color='k', picker=0, url=num)
                total_line_entities_dict[num] = saved_line_entities_dict[num]
                # print('saved num is {}'.format(num))
                # procing_line_entities_dict[
                #     num] = entity_in_map  # 传递的是line_entity,为了统计全部的entities,先把数据传进去
            else:
                line = entity_in_map.draw(color='b', picker=5, url=num)
                total_line_entities_dict[num] = entity_in_map
                print('no saved num is {}'.format(num))
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

    # 保存line_entities_dict.json
    if len(zhenjiang_map.done_line_entity_dict) > 0:
        jft.saveLineMapToJson(inout_entities_map_file, 'w+',
                              zhenjiang_map.done_line_entity_dict)
    else:
        print('no line_entity selected.')

    # 保存参考线地图
    if len(zhenjiang_map.ref_line_dict) > 0:
        out_ref_line_map_file = input(
            '请输入参考线地图文件名称,回车默认为:{}_ref_line_map.json'.format(file_dir))
        if len(out_ref_line_map_file) == 0:
            out_ref_line_map_file = file_dir + '_ref_line_map.json'
        else:
            out_ref_line_map_file = file_dir + out_ref_line_map_file

        # 读取ref_line_map.json,查看id,如果id存在map.ref_line_dict中,那么删除该行
        try:
            pf = open(out_ref_line_map_file, 'r+')
            lines = csv.reader(pf)
            surv_lines = []
            for line in lines:
                id = int(line[0])
                if not zhenjiang_map.ref_line_dict.__contains__(
                        id):  # 已经保存的id不在本次地图生成范围,则保留
                    print(id)
                    surv_lines.append(line)
            pf.truncate(0)
            writer = csv.writer(pf)
            writer.writerows(surv_lines)
        except FileNotFoundError as e:
            print('file not exist!')
        finally:
            pf.close()

        saveRefLineToFile(out_ref_line_map_file, zhenjiang_map.ref_line_dict,
                          'a+')  # 保存新数据

    # 确认全部entity都已经连接
    if len(zhenjiang_map.done_line_entity_dict) == num:
        out_connect_map_file = input(
            '请输入有向连通地图文件名称,回车默认为:{}_connect_map.json'.format(file_dir))
        if len(out_connect_map_file) == 0:
            out_connect_map_file = file_dir + '_connect_map.json'
        else:
            out_connect_map_file = file_dir + out_connect_map_file
        connect_map_dict = getConnectMap(saved_line_entities_dict, 2 * scale)
        saveConnectMapTofile(out_connect_map_file, connect_map_dict)
