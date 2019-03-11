# # -*- coding:utf-8 -*-

# import numpy as np
# import matplotlib.pyplot as plt
# import scipy.spatial as spt

# class ModifyMap:
#   def __init__(self, fig, gps_map):
#     self.map_tree = spt.KDTree(gps_map)
#     self.fig = fig
#     self.begin_point = ()
#     self.end_point = ()
#     self.road_id = 0
#     self.road_id_list = []
#     self.ref_line = []
#     self.ref_line_dict = {}
#     self.ax = self.fig.gca()
#     self.ann = self.ax.annotate("", xy=(0,0), xytext=(-50,50), textcoords="offset pixels", 
#                       bbox=dict(boxstyle="round", fc='r'), arrowprops=dict(arrowstyle="<->"))
#     self.button = 0
  
#   def onButtonPress(self, event):
#     if event.button == 1: # left click
#       x = event.xdata
#       y = event.ydata
#       # seek point
#       (dis, nearest_point_index) = self.map_tree.query((x, y))
#       self.nearest_points = self.map_tree.data[nearest_point_index]
#       # set point
#       if len(self.begin_point) == 0: # begin
#         self.begin_point = self.nearest_points
#         self.ann.xy = self.begin_point
#         self.ann.set_text("right click to repick start")
#         self.ann.set_visible(True)
#         event.canvas.draw_idle()
#         print("start")
#       else:
#         if len(self.end_point) == 0: # end
#           self.end_point = self.nearest_points
#           self.ann.xy = self.end_point
#           self.ann.set_text("right click to repick end")
#           self.ann.set_visible(True)
#           event.canvas.draw_idle()
#           print("end")
#         else: # save to vect
#           self.ann.xy = (event.xdata, event.ydata)
#           self.ann.set_text("save ref_line")
#           self.ann.set_visible(True)
#           event.canvas.draw_idle()
#           self.end_point = []
#           self.begin_point = []
#           #save data
#           print("save")
#     else: # right click
#       if len(self.end_point)>0:
#         self.ann.xy = self.begin_point
#         self.ann.set_text("repick the end point")
#         self.ann.set_visible(True)
#         event.canvas.draw_idle()
#         self.end_point = []
#         print("re_end")
#       else:
#         if len(self.begin_point)>0:
#           self.ann.set_visible(False)
#           event.canvas.draw_idle()
#           self.end_point = []
#           self.begin_point = []
#           print("re_start")

#   def onButtonRelease(self, event):
#     return
  
#   def callBackConnect(self):
#     self.fig.canvas.mpl_connect('button_press_event', self.onButtonPress)
#     self.fig.canvas.mpl_connect('button_release_event', self.onButtonPress)
#     return

#   def callBackDisconnect(self):
#     self.fig.canvas.mpl_disconnect('pick_event', self.onPick)
#     self.fig.canvas.mpl_disconnect('button_press_event', self.onButtonPress)
#     self.fig.canvas.mpl_disconnect('button_release_event', self.onButtonPress)
#     return

# """##############################################
# """
# if __name__ == "__main__":
#   direct = "../data/GPS_info/"
#   coordi_type = "gps_"
#   namelist = ['b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

#   """
#   # read data from files
#   """
#   filename = coordi_type + "a" + ".txt" + ".txt"
#   data = np.loadtxt(direct+filename, delimiter='\t', usecols=[1,2])

#   for alphabet in namelist:
#     filename = coordi_type + alphabet + ".txt" + ".txt"
#     try:
#       data1=np.loadtxt(direct+filename, delimiter='\t', usecols=[1,2])
#     except IOError:
#       print("file open failed")
#       break
    
#     if(data1.size!=0):
#       data = np.concatenate((data, data1), axis=0)
#     else:
#       print("%s is empty file!" %(filename))
    
#     print("now loading {}".format(filename))
  
#   """
#   # transfer from gps to xyz
#   """
#   xyz_map = data*111000 # need modified

#   """################################################################################
#   # matplot
#   # 1.对数据分两个维度分别进行排序
#   # 2.绘图
#   # 3.左键选起始点，右键取消
#   # 4.左键选结束点，右键取消
#   # 5.保存
#   """

#   fig = plt.figure("basic_map")

#   map_tree = spt.KDTree(xyz_map)
#   print(map_tree.data.shape)

#   x = xyz_map[:, 0]
#   y = xyz_map[:, 1] 
#   plt.plot(x, y, 'o')

#   map_mod = ModifyMap(fig, xyz_map)
#   map_mod.callBackConnect()

#   plt.show()

# -*- coding:utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import scipy.spatial as spt

class ModifyMap:
  def __init__(self, fig, gps_map):
    self.map_tree = spt.KDTree(gps_map)
    self.fig = fig
    self.road_point = []
    self.road_point_id = 0
    self.road_point_list = []
    self.ax = fig.gca()
    self.annt_list = []
  
  def onPick(self, event):
    mousevent = event.mouseevent
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    points = tuple(zip(xdata[ind], ydata[ind]))
    print('onpick points:', points)
    if mousevent.button == 1: # if left_button pressed, add the point to road_point_list
      self.road_point = points[0] #
      self.road_point_id = self.road_point_id + 1
      self.road_point_list.append(self.road_point) 
      plt.plot(self.road_point[0], self.road_point[1], 'ro')
      self.drawPointID(self.road_point_id-1)
      self.fig.canvas.draw()
      print("{} points in the list".format(self.road_point_id))
    return

  def onButtonPress(self, event):
    if event.button != 1:
      if self.road_point_id>0:
        print("one road point is removed!")
        plt.plot(self.road_point_list[self.road_point_id-1][0], 
                  self.road_point_list[self.road_point_id-1][1], 'bo')
        self.destroyPointID(self.road_point_id-1)
        self.road_point_id = self.road_point_id - 1
        self.road_point_list.pop()
        self.fig.canvas.draw()
      else:
        print("no point in road_point_list")
    return

  def callBackConnect(self):
    self.fig.canvas.mpl_connect('pick_event', self.onPick)
    self.fig.canvas.mpl_connect('button_press_event', self.onButtonPress)
    return

  def callBackDisconnect(self):
    self.fig.canvas.mpl_disconnect('pick_event', self.onPick)
    self.fig.canvas.mpl_disconnect('button_press_event', self.onButtonPress)
    return

  def drawPointID(self, point_index):
    annt = ax.annotate("", xy=(0,0), xytext=(-20,20), textcoords="offset pixels", 
                      bbox=dict(boxstyle="round", fc='r'), arrowprops=dict(arrowstyle="-"))
    annt.set_text(str(point_index))
    annt.xy = self.road_point_list[point_index]
    annt.set_visible(True)
    self.annt_list.append(annt)

  def destroyPointID(self, point_index):
    annt = self.annt_list[point_index]
    annt.remove()
    self.annt_list.pop()

"""##############################################
"""
if __name__ == "__main__":
  direct = "../data/GPS_info/"
  coordi_type = "gps_"
  namelist = ['b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

  """
  # read data from files
  """
  filename = coordi_type + "a" + ".txt" + ".txt"
  data = np.loadtxt(direct+filename, delimiter='\t', usecols=[1,2])

  for alphabet in namelist:
    filename = coordi_type + alphabet + ".txt" + ".txt"
    try:
      data1=np.loadtxt(direct+filename, delimiter='\t', usecols=[1,2])
    except IOError:
      print("file open failed")
      break
    
    if(data1.size!=0):
      data = np.concatenate((data, data1), axis=0)
    else:
      print("%s is empty file!" %(filename))
    
    print("now loading {}".format(filename))
  
  """
  # transfer from gps to xyz
  """
  xyz_map = data*111000 # need modified

  """################################################################################
  # matplot
  # 1.对数据分两个维度分别进行排序
  # 2.绘图
  # 3.左键选起始点，右键取消
  # 4.左键选结束点，右键取消
  # 5.保存
  """


  map_tree = spt.KDTree(xyz_map)
  print(map_tree.data.shape)

  x = xyz_map[:, 0]
  y = xyz_map[:, 1] 
  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.set_title('modify map')
  orig_fig, = ax.plot(x, y, 'o', picker=3)

  map_mod = ModifyMap(fig, xyz_map)
  map_mod.callBackConnect()

  plt.show()

