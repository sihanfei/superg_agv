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
  def __init__(self, fig, gps_map, annt_dict, point_dict):
    self.fig = fig
    self.total_points = gps_map.tolist()
    self.connect_point = []
    self.connect_point_dict = point_dict
    self.annt_dict = annt_dict
    self.connect_point_id_list = []
    self.connect_point_list = []
    if len(point_dict) > 0:
      for ind, ID in enumerate(point_dict):
        self.connect_point_id_list.append(ID)
        self.connect_point_list.append(point_dict[ID])
      self.connect_point_id = self.connect_point_id_list[-1]
    else:
      self.connect_point_id = 0
      self.connect_point_list = []
    self.ax = fig.gca()
    self.ax.set_title("'v' to get ref_line")
    self.get_ref_line_flag = False
    self.connect_tree = []
    # ref_line
    self.start_point = ()
  
  def onPick(self, event):
    mousevent = event.mouseevent
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    points = tuple(zip(xdata[ind], ydata[ind]))

    if not self.get_ref_line_flag:
      if mousevent.button == 1: # if left_button pressed, add the point to connect_point_list
        self.connect_point = points[-1] # get point
        self.connect_point_id = self.connect_point_id + 1 # set point_id
        self.drawPointID(self.connect_point_id, self.connect_point)
        print("{} points in the list".format(len(self.connect_point_id_list)))
      else: # right select will delete the point
        connect_point = self.getSamePoint(points, self.connect_point_list)
        if connect_point != 0:
          connect_point_id = list(self.connect_point_dict.keys()) [list(self.connect_point_dict.values()).index (connect_point)]
          self.destroyPointID(connect_point_id)
        pass
    else:
      if mousevent.button == 1:
        
        pass
      else:
        pass
    return

  def getSamePoint(self, list1, list2):
    list_a = [a for a in list1 if a in list2]
    if len(list_a) > 0:
      return list_a[0]
    else:
      return 0

  def onButtonPress(self, event):
    if self.get_ref_line_flag:
      if event.button == 1:
        point_click = (event.xdata, event.ydata)
        if len(self.start_point) == 0:
          _, tree_ind = self.connect_tree.query(point_click)
          self.start_point = self.connect_tree.data[tree_ind]
          list_ind = self.connect_point_list.index(self.start_point)
          print("in the list, ind is {}".format(list_ind))
        pass
    else:
      pass
    return

  def onKeyPress(self, event):
    if event.key == 'v' and not self.get_ref_line_flag:
      print "sa'v'e map"
      self.connect_tree = spt.KDTree(self.connect_point_list)
      self.get_ref_line_flag = True
      self.ax.set_title("pick to draw ref_line")
      self.fig.canvas.draw()
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

  def drawPointID(self, point_ID, connect_point):
    # add the point/ID/annotate
    self.connect_point_id_list.append(point_ID) 
    self.connect_point_list.append(connect_point) 
    self.connect_point_dict[point_ID] = connect_point
    plt.plot(connect_point[0], connect_point[1], 'r.')
    annt = ax.annotate("", xy = (0,0), xytext = (-20,20), textcoords = "offset pixels", 
                      bbox = dict(boxstyle = "round", fc = 'r'), arrowprops = dict(arrowstyle = "-"))
    annt.set_text(str(point_ID))
    annt.xy = connect_point
    annt.set_visible(True)
    self.annt_dict[point_ID] = annt
    self.fig.canvas.draw()

  def destroyPointID(self, point_ID):
    connect_point = self.connect_point_dict[point_ID]
    # remove the point/the id/annotate
    del(self.connect_point_dict[point_ID])
    self.connect_point_list.remove(connect_point)
    self.connect_point_id_list.remove(point_ID)
    if len(self.connect_point_id_list) == 0:
      self.connect_point_id = 0
    else:
      self.connect_point_id = self.connect_point_id_list[-1]
    annt = self.annt_dict[point_ID]
    del(self.annt_dict[point_ID])
    annt.remove()
    plt.plot(connect_point[0], connect_point[1], 'g.') # overwrite the point
    self.fig.canvas.draw()

"""##############################################
"""
if __name__ == "__main__":
  """#################################################################
  # 准备进行接续点的选择
  """
  direct = "../data/GPS_info/"
  filename = "map_point_data.csv"

  xyz_map = np.loadtxt(direct+filename, delimiter=',')
  xyz_map = np.unique(xyz_map, axis=0) # 去重
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
  if len(map_modi.connect_point_id_list)>0:
    output = open('point_id_list.csv', 'w')
    try:
      np.savetxt(output, map_modi.connect_point_id_list, fmt = '%d', delimiter = ',', newline = '\n')
    finally:
      output.close()
    
    output = open('point_list.csv', 'w')
    try:
      np.savetxt(output, map_modi.connect_point_list, fmt = '%f', delimiter = ',', newline = '\n')
    finally:
      output.close()
  
  print("{} points".format(len(map_modi.connect_point_id_list)))



