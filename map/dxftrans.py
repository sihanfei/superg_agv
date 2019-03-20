# # -*- coding:utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.lines as ln
import PIL.Image as PIImg
import scipy.spatial as spt
import dxfgrabber as grb

import JsonFormat as jft

connect_dt = np.dtype([
    ('end_point_ID', np.int16), 
    ('ref_line_ID', np.int16), 
    ('ref_line_length', np.float), 
    ('speed_limited', np.int32)])


class ModifyMap:
  """
  {ref_line_ID:ref_line} 参考线地图
  {start_point_ID: (end_point_ID, ref_line_ID, ref_line_length, speed_limited)} 连通地图
  """
  def __init__(self, fig, entity_dict):
    self.fig = fig
    self.entity_dict = entity_dict
    self.draw_entity_list = [] # 按照顺序存储选择的entity
    self.draw_artist_list = []
    # 
    self.ref_line_id_list = []
    self.ref_line = []
    self.ref_line_dict = {} # 参考线地图 {ref_line_id : ref_line=(point, theta, cuv, gcuv, width, distance)}
    self.connect_map_dict = {} # 连通地图 {start_point: (end_point, ref_line_id, ref_line_length, speed_limited)}
    self.ref_line_gps_dict = {} # {ref_line_id : gps_points}
    # 
    self.picker = ''
    self.start_point = []
    
  def onPick(self, event):
    mousevent = event.mouseevent
    artist = event.artist
    if mousevent.button == 1:
      if self.picker == 'start_point':
        if artist in self.draw_artist_list:
          m_point = [mousevent.xdata, mousevent.ydata]
          print('m = {}'.format(m_point))
          data = artist.get_xydata()
          p0 = data[0]
          p1 = data[-1]
          dis0 = self.calcDistance(p0, m_point)
          dis1 = self.calcDistance(p1, m_point)
          print('p0 = {}, d0={}, p1={}, d1 = {}'.format(p0, dis0, p1, dis1))
          if dis0 <= dis1:
            self.start_point = p0
          else:
            self.start_point = p1
          ax = self.fig.gca()
          ax.set_title("'v' to save")
          self.setAnntOnPoint('p', self.start_point, True)
      else:
        entity_id = int(artist.get_url())
        self.draw_entity_list.append(self.entity_dict[entity_id])
        self.draw_artist_list.append(artist)
        artist.set_color('k')
      self.fig.canvas.draw()
    else:
      if len(self.draw_entity_list) > 0:
        artist.set_color('b')
        entity_id = int(artist.get_url())
        self.draw_entity_list.remove(self.entity_dict[entity_id])
        self.draw_artist_list.remove(artist)
        self.fig.canvas.draw()
    # # print('draw list len = {}, artist len = {}'.format(len(self.draw_entity_list), len(self.draw_artist_list)))

  def scatterLine(self, entity): # 将一个entity 进行离散化,并计算各个参考点属性
    scatter_point = []
    scatter_gps = []

    if entity.dxftype == 'LINE':
      start_point, end_point = entity.start, entity.end
      d = self.calcDistance(start_point, end_point)
      delta_x = (end_point[0] - start_point[0])/d
      delta_y = (end_point[1] - start_point[1])/d
      if delta_x==0 and delta_y == 0:
        x = start_point[0]
        y = start_point[1]
      elif delta_x != 0 and delta_y == 0:
        x = np.arange(start_point[0], end_point[0]+delta_x, delta_x)
        y = np.ones(x.shape)*start_point[1]
      elif delta_x == 0 and delta_y != 0:
        y = np.arange(start_point[1], end_point[1]+delta_y, delta_y)
        x = np.ones(y.shape)*start_point[0]
      else:
        x = np.arange(start_point[0], end_point[0], delta_x)
        y = np.arange(start_point[1], end_point[1], delta_y)
      # np.insert(x, -1, end_point[0])
      # np.insert(y, -1, end_point[1])
      print('scatterLine: {}'.format(len(x)))
      for i in range(len(x)):
        ref_point = jft.RefPointPara()
        ref_point.setCuv(0)
        ref_point.setGcuv(0)
        ref_point.setWidth(tuple([2, 2]))
        ref_point.setTheta(np.arctan((y[1]-y[0])/(x[1]-x[0])))
        distance_s = np.sqrt((x[i] - x[0]) ** 2 + (y[i] - y[0]) ** 2)
        ref_point.setPoint(tuple([x[i], y[i]]))
        ref_point.setS(distance_s)
        scatter_point.append(ref_point)
        scatter_gps.append(ref_point.point)
      pass
    elif entity.dxftype == 'ARC':
      center_point = entity.center
      radius = entity.radius
      start_angle = entity.start_angle
      end_angle = entity.end_angle
      if end_angle == 0:
        end_angle = 360
      delta_angle = (end_angle - start_angle)/360 # 按照1度为基准转换
      angle_array = np.arange(start_angle, end_angle+delta_angle, delta_angle)*np.pi/180
      x = np.cos(angle_array)*radius + center_point[0]
      y = np.sin(angle_array)*radius + center_point[1]
      for i in range(len(x)):
        ref_point = jft.RefPointPara()
        ref_point.setCuv(1/radius)
        ref_point.setWidth(tuple([-2, 2]))
        distance_s = np.sqrt((x[i] - x[0]) ** 2 + (y[i] - y[0]) ** 2)
        ref_point.setPoint(tuple([x[i], y[i]]))
        if i == 0:
          ref_point.setGcuv(ref_point.cuv / distance_s)
        else:
          ref_point.setGcuv(0)
        ref_point.setTheta(angle_array[i] - np.pi/2)
        scatter_point.append(ref_point)
        scatter_gps.append(ref_point.point)
      pass
    else:
      pass
    print('scatterLine:point:s={}, e={}'.format(scatter_point[0].point, scatter_point[-1].point))
    print('scatterLine:gps:s={}, e={}'.format(scatter_gps[0], scatter_gps[-1]))
    return list(scatter_point), list(scatter_gps)

  def pointsListNeedSort(self, start_end_list, start_point): 
    # 根据起点和终点的相互关系对点集进行重新排序:
    # 前提假定:第一个点集是确定的起点
    # 之后的每个点集都是按照顺序连接的,只是起终点不确定
    sort_list = [] # 如果需要重排序,则为真,否则为假
    for points in start_end_list:
      start = points[0]
      end = points[1]
      dis0 = self.calcDistance(start_point, start)
      dis1 = self.calcDistance(start_point, end)
      if dis0 <= dis1:
        sort_list.append(False)
        start_point = start
      else:
        sort_list.append(True)
        start_point = end
    return sort_list

  def switchStartandEnd(self, entity):
    if entity.dxftype == 'LINE':
      entity.start, entity.end = entity.end, entity.start
    elif entity.dxftype == 'ARC':
      entity.start_angle, entity.end_angle = entity.end_angle, entity.start_angle
      pass
    else:
      pass
    return entity

  def calcDistance(self, p1, p2):
    distance = np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
    return distance

  def getPointsOfEntity(self, entity):
    points = []
    if entity.dxftype == "LINE":
      ps = entity.start
      pe = entity.end
    elif entity.dxftype == 'ARC':
      r = entity.radius
      pc = entity.center
      sangle = entity.start_angle*np.pi/180.0
      eangle = entity.end_angle*np.pi/180.0
      ps = pc + [r*np.cos(sangle), r*np.sin(sangle)]
      pe = pc + [r*np.cos(eangle), r*np.sin(eangle)]
    else:
      ps = []
      pe = []
      pass
    points = [ps, pe]
    return points

  def drawPoint(self, point, color):
    # print('draw_point is {}'.format(point))
    plt.plot(point[0], point[1], color)

  def getRefLineFromEntityList(self, draw_entity_list):
    ref_line = list([]) # 一条完整的参考线
    gps_line = list([])
    # 将entity转换为起点和终点
    start_end_list = []
    for entity in draw_entity_list:
      start_end_list.append(self.getPointsOfEntity(entity))
    # 对起点和终点是否需要交换进行判断
    switch_list = self.pointsListNeedSort(start_end_list, self.start_point)
    # 根据entity计算参考点的各个参数,并根据是否需要交换进行点集序列的重排
    for i in range(len(switch_list)):
      ref_points, gps_points = self.scatterLine(self.draw_entity_list[i]) # 每个entity形成的参考点集
      if switch_list[i]:
        ref_points.reverse()
        gps_points.reverse()
      ref_line = ref_line + ref_points
      gps_line = gps_line + gps_points
    print('getRefLineFromEntityList: s={}, e={}'.format(ref_line[0].point, ref_line[-1].point))
    return list(ref_line), gps_line
  
  def saveRefLineToMap(self, ref_line):
    if len(self.ref_line_id_list) == 0:
      ref_line_id = 1
    else:
      ref_line_id = self.ref_line_id_list[-1] + 1
    # 存储
    self.ref_line_id_list.append(ref_line_id)
    self.ref_line_dict[ref_line_id] = ref_line
    start_point = ref_line[0].getPoint()
    end_point = ref_line[-1].getPoint()
    ref_line_length = ref_line[-1].getS()
    speed_limited = 60.0
    new_value = [end_point, ref_line_id, ref_line_length, speed_limited]
    if start_point in self.connect_map_dict:
      value = self.connect_map_dict[start_point]
    else:
      value = list([])
    self.connect_map_dict[start_point] = value.append(new_value) # 连通地图 {start_point: (end_point, ref_line_id, ref_line_length, speed_limited)}
    # 清空
    self.draw_artist_list.clear()
    self.draw_entity_list.clear()
    return

  def onButtonPress(self, event):
    pass

  def addRoadToConnect(self):
    pass

  def onKeyPress(self, event):
    if event.key == 'v':
      # # print('saving')
      if len(self.draw_artist_list) == 0 and len(self.start_point) == 0:
        return
      ref_line, _ = self.getRefLineFromEntityList(self.draw_entity_list)
      self.saveRefLineToMap(ref_line)
      self.addRoadToConnect()
      
      jft.saveJsonFile('ref_line.json', 'a+', self.ref_line_dict)

      
      # 在终点处设置标签
      print('ref-line len={}'.format(len(ref_line)))
      road_point = ref_line[-1].point
      self.setAnntOnPoint('E', road_point, True)
      road_point = ref_line[0].point
      self.setAnntOnPoint('S', road_point, True)
      
      self.start_point = []
      self.picker = ''
      ax = self.fig.gca()
      ax.set_title("'b' to pick start")
      self.fig.canvas.draw()
    # pick begin
    elif event.key == 'b':
      if len(self.draw_artist_list) == 0:
        return
      self.picker = 'start_point'
      for artist in self.draw_artist_list:
        artist.set_color('r')
      pass
      self.fig.canvas.draw()
    else:
      # # print('No This Command')
      pass

  def setAnntOnPoint(self, text, point, status):
    ax = self.fig.gca()
    annt = ax.annotate("", xy=(0,0), xytext=(-20,20), textcoords="offset pixels", 
                      bbox=dict(boxstyle="round", fc='r'), arrowprops=dict(arrowstyle="-"))
    annt.set_text(text)
    annt.xy = point
    annt.set_visible(status)


  def callBackConnect(self):
    self.fig.canvas.mpl_connect('pick_event', self.onPick)
    self.fig.canvas.mpl_connect('button_press_event', self.onButtonPress)
    self.fig.canvas.mpl_connect('key_release_event', self.onKeyPress)

  def callBackDisconnect(self):
    self.fig.canvas.mpl_disconnect(self.onPick)
    self.fig.canvas.mpl_disconnect(self.onButtonPress)
    self.fig.canvas.mpl_disconnect(self.onKeyPress)


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
  ax.set_title("'b' pick start")

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
        entity.start = (np.array(entity.start)/1000-bias) * scale
        entity.end = (np.array(entity.end)/1000-bias) * scale
        start_point = entity.start
        end_point = entity.end
        # x = (np.array([start_point[0], end_point[0]])/1000 - bias[0]) * scale
        # y = (np.array([start_point[1], end_point[1]])/1000 - bias[1]) * scale
        x = np.array([start_point[0], end_point[0]])
        y = np.array([start_point[1], end_point[1]])
        # # print('x={}'.format(x))
        # 利用line的url属性传递entity的id信息
        aline = ln.Line2D(x, y, url = str(ref_seg_id), picker = 3, color = 'b')
        ax.add_line(aline)
      if entity.dxftype == 'ARC':
        entity.center = (np.array(entity.center)/1000.0-bias) * scale
        entity.radius = entity.radius/1000.0*scale
        radius = entity.radius
        center_point = entity.center
        radius = entity.radius
        start_angle = entity.start_angle
        end_angle = entity.end_angle
        if end_angle == 0:
          end_angle = 360.0
        # # # print('start = {}, end = {}'.format(start_angle, end_angle))
        delta_angle = (end_angle - start_angle)/360.0 # 按照1度为基准转换
        angle_array = np.arange(start_angle, end_angle+delta_angle, delta_angle)*np.pi/180.0
        x = (np.cos(angle_array)*radius + center_point[0])
        y = (np.sin(angle_array)*radius + center_point[1])
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

