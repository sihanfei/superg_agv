# # -*- coding:utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import PIL.Image as PIImg
import scipy.spatial as spt


"""
# 选择接续点的工具类
"""
class ModifyMap:
    def __init__(self, fig, gps_map):
        self.fig = fig
        self.total_tree = spt.KDTree(gps_map)
        # 连接点
        self.connect_point_id = []
        self.connect_point = []
        self.connect_point_dict = {}
        self.connect_tree = []
        # 绘图元素
        self.ax = fig.gca()
        self.annt = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(-20, 20),
            textcoords="offset pixels",
            bbox=dict(boxstyle="round", fc='r'),
            arrowprops=dict(arrowstyle="-"))        
        self.ax.set_title("now type is line")
        self.get_ref_line_flag = False
        self.annt_dict = {}
        self.line_type = 'line'
        # ref_line
        self.start_point = ()
        self.draw_start = ()
        self.start_point_ID = []
        self.draw_point_list = []
        self.mid_point = ()
        self.mid_point_ID = []
        self.end_point = ()
        self.end_point_ID = []
        self.ref_line = []
        self.ref_line_part = []
        self.ref_line_id_list = []
        self.ref_line_list = []
        self.ref_line_dict = {}

    def onPick(self, event):
        mousevent = event.mouseevent
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        index = event.ind
        points = tuple(zip(xdata[index], ydata[index]))

        if mousevent.button == 1:
            point = points[0]
            point = tuple([point[0], point[1]])
            plt.plot(point[0], point[1], 'r.')
            self.annt.xy = point
            self.annt.set_visible(True)
            self.draw_point_list.append(point)
            if self.line_type == 'line':
                if len(self.draw_point_list) == 1:
                    self.annt.set_text('Start')
                elif len(self.draw_point_list) >= 2:
                    self.annt.set_text('End')
                    self.ref_line_part = self.getRefLine(self.draw_point_list[-2], self.draw_point_list[-1], 'line')
                    self.drawPoints(self.ref_line_part, 'r.')
                    self.ref_line = self.ref_line + self.ref_line_part
                    print(self.ref_line)
                pass
            elif self.line_type == 'circle':
                pass
            else:
                pass
        else:
            print('repick')
            if len(self.draw_point_list) >= 2:
                print(self.draw_point_list[-1])
                index_s = self.ref_line.index(self.draw_point_list[-1])
                index_e = self.ref_line.index(self.draw_point_list[-2])
                draw_list = self.draw_point_list[index_s:index_e:-1]
                self.drawPoints(draw_list, 'b.')
                self.draw_point_list.pop()
                self.annt.xy = self.draw_point_list[-1]
                if len(self.draw_point_list) == 1:
                    self.annt.set_text('Start')
            elif len(self.draw_point_list) == 1:
                self.draw_point_list.pop()
                self.annt.set_visible(False)
            pass
        self.fig.canvas.draw()
        return

    def getRefLine(self, ps, pe, method):
        ref_line = []
        if method == 'line':
            print('draw a line')
            diff = np.array(pe) - np.array(ps)
            distance = np.sqrt((diff[0])**2 + (diff[1])**2)
            number = int(distance/1) # 按照1m间隔采样点
            for i in range(number):
                point = ps + diff/number*i
                ref_line.append(point)
                # plt.plot(point[0], point[1], 'r.')
            ref_line.append(pe)
            pass
        elif method == 'circle':
            pass
        else:
            pass
        return ref_line

    def getSamePoint(self, list1, list2):
        list_a = [a for a in list1 if a in list2]
        if len(list_a) > 0:
            return list_a[0]
        else:
            return 0

    def onButtonPress(self, event):
        return

    def onKeyPress(self, event):

        return

    def calcCircle(self, point1, point2):
        
        return

    def saveRefLine(self, ref_line):
        return

    def callBackConnect(self):
        self.fig.canvas.mpl_connect('pick_event', self.onPick)
        self.fig.canvas.mpl_connect('button_press_event', self.onButtonPress)
        self.fig.canvas.mpl_connect('key_release_event', self.onKeyPress)
        return

    def callBackDisconnect(self):
        self.fig.canvas.mpl_disconnect(self.onPick)
        self.fig.canvas.mpl_disconnect(self.onButtonPress)
        self.fig.canvas.mpl_disconnect(self.onKeyPress)
        return

    def drawPoints(self, points, color):
        if len(points) > 0:
            for point in points:
                # print(point)
                plt.plot(point[0], point[1], color)
        self.fig.canvas.draw()

    def drawPointID(self, point_ID, connect_point):
        return

    def destroyPointID(self, point_ID):
        return


"""##############################################
"""
if __name__ == "__main__":
    """#################################################################
  # 准备进行接续点的选择
  """
    direct = "../data/GPS_info/"
    filename = "map_point_data.csv"

    xyz_map = np.loadtxt(direct + filename, delimiter=',')
    xyz_map = np.unique(xyz_map, axis=0)  # 去重
    img1 = PIImg.open(direct + "zhenjiang.bmp")
    npimg1 = np.array(img1)
    npimg1 = npimg1[-1:0:-1, :, :]
    scale = 1 / 0.116
    bias = [18.75, -0.75]
    xyz_map = (xyz_map - bias) * scale  # 针对镇江地图的偏移

    # 准备绘图
    x = xyz_map[:, 0]
    y = xyz_map[:, 1]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('modify map')
    ax.plot(x, y, 'g.', picker=5)

    # 显示并关联到选点程序
    ax.imshow(npimg1, origin='lower')
    ax.autoscale(False)
    map_modi = ModifyMap(fig, xyz_map)
    map_modi.callBackConnect()
    plt.show()

    # 断开连接，保存接续点数据

    # print("{} points".format(len(map_modi.connect_point_id_list)))
