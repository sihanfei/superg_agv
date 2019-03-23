import csv as csv
import networkx as nx
import matplotlib.pyplot as plt
import PIL.Image as PIImg
import numpy as np


def getConnectMapFromJson(filename):
    connect_map_dict = {}
    try:
        fp = open(filename, 'r')
        connect_map = csv.reader(fp)
        for item in connect_map:
            value = []
            for i in range(2, len(item)):
                value.append(int(item[i]))
            connect_map_dict[int(item[0])] = value
    except FileExistsError:
        return False
    finally:
        fp.close()
    return connect_map_dict


def getRefLinePointMapFromJson(filename):
    try:
        fp = open(filename, 'r')
        ref_line_map = csv.reader(fp)
        ref_line_point_map_dict = {}
        ref_line_ID = 0
        # ref_line_speed_limited = []
        for item in ref_line_map:  # 每一行就是一个点，需要通过每行前的id号判断是否是同一条参考线
            point = tuple((float(item[1]), float(item[2])))
            if ref_line_ID == 0:  # 第一个数据
                ref_line_ID = int(item[0])
                point_list = []
                point_list.append(point)
                ref_line_point_map_dict[ref_line_ID] = point_list
            else:
                if ref_line_ID != int(item[0]):  # 新的ref line
                    ref_line_ID = int(item[0])
                    point_list = []
                    point_list.append(point)
                    ref_line_point_map_dict[ref_line_ID] = point_list
                else:
                    point_list.append(point)
                    ref_line_point_map_dict[ref_line_ID] = point_list

            point = tuple((float(item[1]), float(item[2])))
            pass
    except FileExistsError:
        return False
    finally:
        fp.close()
    return ref_line_point_map_dict


def getRefLineLengthMapFromJson(filename):
    try:
        fp = open(filename, 'r')
        ref_line_map = csv.reader(fp)
        ref_line_length_map_dict = {}
        ref_line_ID = []
        ref_line_length = []
        # ref_line_speed_limited = []
        for item in ref_line_map:  # 每一行就是一个点，需要通过每行前的id号判断是否是同一条参考线
            ref_line_ID = int(item[0])
            ref_line_length = float(item[3])
            ref_line_length_map_dict[
                ref_line_ID] = ref_line_length  # 利用了两个特性：字典的key唯一，ref_line的长度是递增的
    except FileExistsError:
        return False
    finally:
        fp.close()
    return ref_line_length_map_dict


if __name__ == "__main__":
    connect_map_file = "../data/map/zhenjiang/connect_map.json"
    connect_map_dict = getConnectMapFromJson(connect_map_file)
    for _, key in enumerate(connect_map_dict):
        print('main:{}:{}'.format(key, connect_map_dict[key]))

    ref_line_map_file = "../data/map/zhenjiang/ref_line_map.json"
    ref_line_length_map_dict = getRefLineLengthMapFromJson(ref_line_map_file)
    for _, key in enumerate(ref_line_length_map_dict):
        print('main:ref_line->{}:{}'.format(key,
                                            ref_line_length_map_dict[key]))

    # 通过networkx画连通图
    G = nx.DiGraph()
    for _, key in enumerate(connect_map_dict):
        value = connect_map_dict[key]
        for nextID in value:
            print('main: for nextID:{}:{}'.format(key, nextID))
            # 需要走过的是车辆所在的ID，所以用所在车道的长度来度量经过的路程
            G.add_weighted_edges_from(
                [(key, nextID, ref_line_length_map_dict[key])],
                weight='length')

    img1 = PIImg.open("../data/map/zhenjiang/zhenjiang.bmp")
    npimg1 = np.array(img1)
    npimg1 = npimg1[-1:0:-1, :, :]
    # 准备绘图
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(npimg1, origin='lower')
    ax.autoscale(False)

    try:
        path = nx.shortest_path(G, 34, 33, weight='length')
        length = nx.shortest_path_length(G, 34, 33, weight='length')
        print('path:{}, length:{}'.format(path, length))
    except nx.NetworkXNoPath:
        print('No path')
    finally:
        ref_line_point_map_dict = getRefLinePointMapFromJson(ref_line_map_file)
        for id in path:
            points = ref_line_point_map_dict[id]
            for p in points:
                plt.plot(p[0], p[1], 'r.')
            # plt.plot()
        plt.show()