# # -*- coding:utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import scipy.spatial as spt
import matplotlib.image as mpimg
import numpy as np
import PIL.Image as PIImg

class prepareData:
  def __init__(self, data_dir):
    self.data_dir = data_dir
    return
  
  def proceedMap(self):
    filename = self.data_dir + "map_point_data.csv"
    try:
      point_data = np.loadtxt(filename, delimiter=',')
      longi = point_data[:,0]
      lanti = point_data[:,1]
      longi_uni, index = np.unique(longi, return_index=True)
      lanti_uni = lanti[return_index]
    except IOError:
      print("cannot open file")
      return False
    return True

"""
# 选择接续点的工具类
"""
class ModifyMap:
  def __init__(self, fig, gps_map, annt_dict, point_dict):
    self.map_tree = spt.KDTree(gps_map)
    self.fig = fig
    self.road_point = []
    self.road_point_dict = point_dict
    self.annt_dict = annt_dict
    self.road_point_id_list = []
    self.road_point_list = []
    if len(point_dict) > 0:
      for ind, ID in enumerate(point_dict):
        self.road_point_id_list.append(ID)
        self.road_point_list.append(point_dict[ID])
      self.road_point_id = self.road_point_id_list[-1]
    else:
      self.road_point_id = 0
      self.road_point_list = []
    self.ax = fig.gca()
  
  def onPick(self, event):
    mousevent = event.mouseevent
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    points = tuple(zip(xdata[ind], ydata[ind]))

    if mousevent.button == 1: # if left_button pressed, add the point to road_point_list
      self.road_point = points[-1] # get point
      self.road_point_id = self.road_point_id + 1 # set point_id
      self.drawPointID(self.road_point_id, self.road_point)
      print("{} points in the list".format(len(self.road_point_id_list)))
    else: # right select will delete the point
      road_point = self.getSamePoint(points, self.road_point_list)
      if road_point != 0:
        road_point_id = list(self.road_point_dict.keys()) [list(self.road_point_dict.values()).index (road_point)]
        self.destroyPointID(road_point_id)
      pass
    return

  def getSamePoint(self, list1, list2):
    list_a = [a for a in list1 if a in list2]
    if len(list_a) > 0:
      return list_a[0]
    else:
      return 0

  def onButtonPress(self, event):
    # if event.button != 1:
    #   if len(self.road_point_id_list)>0:
    #     print("now {} point in list".format(len(self.road_point_id_list)))
    #     print("now id={}".format(self.road_point_id))
    #     self.road_point_id = self.road_point_id_list[-1]
    #     print("refresh id={}".format(self.road_point_id))
    #     self.destroyPointID(self.road_point_id)
    #     print("destroy id={}".format(self.road_point_id))
    #   else:
    #     print("no point in road_point_list")
    return

  def onKeyPress(self, event):
    if event.key == 'v':
      pass
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

  def drawPointID(self, point_ID, road_point):
    # add the point/ID/annotate
    self.road_point_id_list.append(point_ID) 
    self.road_point_list.append(road_point) 
    self.road_point_dict[point_ID] = road_point
    plt.plot(road_point[0], road_point[1], 'r.')
    annt = ax.annotate("", xy = (0,0), xytext = (-20,20), textcoords = "offset pixels", 
                      bbox = dict(boxstyle = "round", fc = 'r'), arrowprops = dict(arrowstyle = "-"))
    annt.set_text(str(point_ID))
    annt.xy = road_point
    annt.set_visible(True)
    self.annt_dict[point_ID] = annt
    self.fig.canvas.draw()

  def destroyPointID(self, point_ID):
    road_point = self.road_point_dict[point_ID]
    # remove the point/the id/annotate
    del(self.road_point_dict[point_ID])
    self.road_point_list.remove(road_point)
    self.road_point_id_list.remove(point_ID)
    if len(self.road_point_id_list) == 0:
      self.road_point_id = 0
    else:
      self.road_point_id = self.road_point_id_list[-1]
    annt = self.annt_dict[point_ID]
    del(self.annt_dict[point_ID])
    annt.remove()
    plt.plot(road_point[0], road_point[1], 'g.') # overwrite the point
    self.fig.canvas.draw()

"""
# 建立连通图的工具类
"""
class SetConnectMap:
  def __init__(self, fig, gps_map, points_dict):
    self.fig = fig
    self.id_list = []
    self.points_list = []
    self.points_dict = points_dict
    for _,ID in enumerate(points_dict):
      self.id_list.append(ID)
      self.points_list.append(points_dict[ID])
    # print(self.id_list)
    # print(self.points_list)
    self.start_point = ()
    self.end_point = ()
    self.road_dict = {}
    self.ref_line_dict = {}
    self.road_id_list = [0]
    return

  def onKeyPress(self, event):
    if event.values == 's':
      if len(self.start_point) > 0 and len(self.end_point) > 0:
        print("seek the ref_line!")
        self.seekRefLine(self.start_point, self.end_point)
        self.txt.remove()
        self.fig.canvas.draw()


  def onButtonPress(self, event):
    if event.button != 1:
      if len(self.end_point) > 0:
        plt.plot(self.end_point[0], self.end_point[1], 'ro')
        self.end_point = ()
        self.txt.remove()
        self.fig.canvas.draw()
      else:
        if len(self.start_point) > 0:
          plt.plot(self.start_point[0], self.start_point[1], 'ro')
          self.start_point = ()
          self.fig.canvas.draw()

  def onPick(self, event):
    mouseevent = event.mouseevent

    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    points = tuple(zip(xdata[ind], ydata[ind]))
    point = points[0]
    if mouseevent.button == 1:
      print(points[0])
      if len(self.start_point) == 0:
        self.start_point = point
        plt.plot(point[0], point[1], 'bo')
        self.fig.canvas.draw()
      else:
        if len(self.end_point) == 0:
          self.end_point = point
          plt.plot(point[0], point[1], 'bo')
          self.txt = plt.text(self.end_point[0]+25, self.end_point[1], "Press 's' to seek, right click to repick", bbox=dict(facecolor='red', alpha=0.5))
          self.fig.canvas.draw()

  """
  # 根据起点和终点，搜寻两点之间的参考点，并保存为参考点集
  """
  def seekRefLine(self, start_point, end_point):
    ref_line = [] # 保存参考点坐标
    
    if len(ref_line) > 0: # 参考线存在
      road_id = self.road_id_list[-1]+1      
      self.road_id_list.append(road_id)
      self.road_dict[road_id] = [start_point, end_point]
      self.ref_line_dict[road_id] = ref_line
    return len(ref_line)

  def callBackConnect(self):
    self.fig.canvas.mpl_connect('pick_event', self.onPick)
    self.fig.canvas.mpl_connect('button_press_event', self.onButtonPress)
    self.fig.canvas.mpl_connect('key_press_event', self.onKeyPress)
    return

  def callBackDisconnect(self):
    self.fig.canvas.mpl_disconnect(self.onPick)
    self.fig.canvas.mpl_disconnect(self.onButtonPress)
    self.fig.canvas.mpl_disconnect(self.onKeyPress)
    return

"""##############################################
"""
if __name__ == "__main__":
  """#################################################################
  # 准备进行接续点的选择
  """
  direct = "../data/GPS_info/"
  filename = "map_point_data.csv"

  xyz_map = np.loadtxt(direct+filename, delimiter=',')
  img1 = PIImg.open(direct+"zhenjiang.bmp")
  npimg1 = np.array(img1)
  npimg1 = npimg1[-1:0:-1,:,:]
  scale = 1/0.116
  bias = [18.75, -0.75]
  xyz_map = (xyz_map-bias)*scale # 针对镇江地图的偏移

  # 读入已经保存的数据地图
  infile = open("point_id_list.csv", 'a+') 
  try:
    point_id_list = np.loadtxt("point_id_list.csv", delimiter=',', usecols=[0])
  finally:
    infile.close()

  infile = open("point_list.csv", 'a+')
  try:
    point_list = np.loadtxt("point_list.csv", delimiter=',')
  finally:
    infile.close()

  # 准备绘图
  x = xyz_map[:, 0]
  y = xyz_map[:, 1] 
  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.set_title('modify map')
  ax.plot(x, y, 'g.', picker = 5)

  # 已经存在数据
  annt_dict = {}
  point_dict = {}
  if len(point_list)>0:
    # 转换点集ID类型
    tmp_point_id_list = []
    for point_id in point_id_list:
      tmp_point_id_list.append(int(point_id))
    point_id_list = tmp_point_id_list

    # 绘制标记点
    ax.plot(point_list[:,0], point_list[:,1], 'r.', picker=5)
    for i in range(len(point_list)):
      annt = ax.annotate("", xy = (0,0), xytext = (-20,20), textcoords = "offset pixels", 
                        bbox = dict(boxstyle = "round", fc = 'r'), arrowprops = dict(arrowstyle = "-"))
      annt.set_text(str(point_id_list[i]))
      annt.xy = point_list[i]
      annt.set_visible(True)
      annt_dict[point_id_list[i]] = annt
      point_dict[point_id_list[i]] = tuple(point_list[i])

    # 转换点集类型
    tmp_point_list = []
    for point in point_list:
      tmp_point_list.append(tuple(point))
    point_list = tmp_point_list
  else:
    point_id_list = []
    point_list = []

  # 显示并关联到选点程序
  ax.imshow(npimg1, origin = 'lower')
  ax.autoscale(False)
  map_modi = ModifyMap(fig, xyz_map, annt_dict, point_dict)
  map_modi.callBackConnect()
  plt.show()

  # 断开连接，保存接续点数据
  map_modi.callBackDisconnect()
  if len(map_modi.road_point_id_list)>0:
    output = open('point_id_list.csv', 'w')
    try:
      np.savetxt(output, map_modi.road_point_id_list, fmt = '%d', delimiter = ',', newline = '\n')
    finally:
      output.close()
    
    output = open('point_list.csv', 'w')
    try:
      np.savetxt(output, map_modi.road_point_list, fmt = '%f', delimiter = ',', newline = '\n')
    finally:
      output.close()
  
  print("{} points".format(len(map_modi.road_point_id_list)))

  """#################################################################
  # 准备进行连通图设计
  """
  if len(map_modi.road_point_id_list)>0:
    # 读入已经保存的数据
    point_id_list = np.loadtxt("point_id_list.csv", delimiter = ',', usecols = [0])
    point_list = np.loadtxt('point_list.csv', delimiter = ',')  
    # 改成int类型
    tmp_point_id_list = []
    for point_id in point_id_list:
      tmp_point_id_list.append(int(point_id))
    point_id_list = tmp_point_id_list
    # 开始绘图
    x = point_list[:,0]
    y = point_list[:,1]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # annotate
    for i in range(len(point_list)):
      annt = ax.annotate("", xy = (0,0), xytext = (-20,20), textcoords = "offset pixels", 
                          bbox = dict(boxstyle = "round", fc = 'r'), arrowprops = dict(arrowstyle = "-"))
      annt.set_text(str(point_id_list[i]))
      annt.xy = point_list[i]
      annt.set_visible(True)
    ax.set_title('connecting map')
    ax.plot(x, y, 'ro', picker = 10)
    # 叠加图片
    ax.imshow(npimg1, origin = 'lower')
    ax.autoscale(False)

    # 进入连接图处理
    set_connect_map = SetConnectMap(fig, xyz_map, point_dict)
    set_connect_map.callBackConnect()
    plt.show()

    set_connect_map.callBackDisconnect()

    # 

  ################  for debug
    map_tree = spt.KDTree(xyz_map) # kd树
