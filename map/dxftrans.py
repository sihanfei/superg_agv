# # -*- coding:utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.lines as ln
import PIL.Image as PIImg
import scipy.spatial as spt
import dxfgrabber as grb


class ModifyMap:
  def __init__(self, fig, entity_dict):
    self.fig = fig
    self.entity_dict = entity_dict
    self.draw_entity_list = [] # 按照顺序存储选择的entity
    
  def onPick(self, event):
    mousevent = event.mouseevent
    artist = event.artist
    if mousevent.button == 1:
      entity_id = int(artist.get_url())
      self.draw_entity_list.append(self.entity_dict[entity_id])
      artist.set_color('k')
      self.fig.canvas.draw()
      print('draw list len = {}'.format(len(self.draw_entity_list)))
    else:
      if len(self.draw_entity_list) > 0:
        artist.set_color('b')
        entity_id = int(artist.get_url())
        self.draw_entity_list.remove(self.entity_dict[entity_id])
        self.fig.canvas.draw()
        print('draw list len = {}'.format(len(self.draw_entity_list)))

  def scatterLine(self, entity): # 将一个entity 进行离散化,并计算各个参考点属性
    if entity.dxftype == 'LINE':
      pass
    elif entity.dxftype == 'CIRCLE':
      pass
    else:
      pass

  def saveARefLine(self):
    pass

  def onButtonPress(self, event):
    # 对点进行排序
    # 离散化
    # 存储
    pass

  def onKeyPress(self, event):
    pass

  def callBackConnect(self):
    self.fig.canvas.mpl_connect('pick_event', self.onPick)
    self.fig.canvas.mpl_connect('button_press_event', self.onButtonPress)
    self.fig.canvas.mpl_connect('key_release_event', self.onKeyPress)

  def callBackDisconnect(self):
    self.fig.canvas.mpl_disconnect(self.onPick)
    self.fig.canvas.mpl_disconnect(self.onButtonPress)
    self.fig.canvas.mpl_disconnect(self.onKeyPress)



class RefPointPara:
  """
  参考点属性结构体
  """
  def __init__(self):
    self.point = []
    self.width = []
    self.cuv = 0
    self.gcuv = 0
    self.s = 0
  
  def calcDistance(self, p1, p2):
    distance = np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
    return distance

  def setWidth(self, width):
    self.width = width
  
  def setCuv(self, cuv):
    self.cuv = cuv
  
  def setGcuv(self, gcuv):
    self.gcuv = gcuv
  
  def setS(self, s):
    self.s = s
  
  def setPoint(self, point):
    self.point = point

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
  ax.set_title("Press 'v' to save")

  # 读取dxf文件
  dxf_object = grb.readfile('map7.dxf')
  
  total_ref_seg_id_list = []
  total_ref_seg_entity = []
  total_ref_seg_dict = {}
  ref_seg_id = 0

  for entity in dxf_object.entities:
    if entity.layer == 'ref_line':
      ref_seg_id = ref_seg_id + 1
      if entity.dxftype == 'LINE': # 对点进行离散化
        start_point = entity.start
        end_point = entity.end
        x = (np.array([start_point[0], end_point[0]])/1000 - bias[0]) * scale
        y = (np.array([start_point[1], end_point[1]])/1000 - bias[1]) * scale
        print('x={}'.format(x))
        aline = ln.Line2D(x, y, url = str(ref_seg_id), picker = 3, color = 'b')
        ax.add_line(aline)
        # ax.plot(x, y, picker = 3 + ref_seg_id/100.0)
      if entity.dxftype == 'ARC':
        center_point = entity.center
        radius = entity.radius
        start_angle = entity.start_angle
        end_angle = entity.end_angle
        if end_angle == 0:
          end_angle = 360
        print('start = {}, end = {}'.format(start_angle, end_angle))
        delta_angle = (end_angle - start_angle)/360 # 按照1度为基准转换
        angle_array = np.arange(start_angle, end_angle+delta_angle, delta_angle)*3.1415926/180
        x = ((np.cos(angle_array)*radius + center_point[0])/1000 - bias[0]) * scale
        y = ((np.sin(angle_array)*radius + center_point[1])/1000 - bias[1]) * scale
        aline = ln.Line2D(x, y, url = str(ref_seg_id), picker = 3, color = 'b')
        ax.add_line(aline)
      total_ref_seg_id_list.append(ref_seg_id)
      total_ref_seg_entity.append(entity)
      total_ref_seg_dict[ref_seg_id] = entity

  # 显示并关联到选点程序
  ax.imshow(npimg1, origin='lower')
  ax.autoscale(False)
  map_modi = ModifyMap(fig, total_ref_seg_dict)
  map_modi.callBackConnect()
  plt.show()

