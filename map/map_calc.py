# /usr/lib/python2.7
# -*- coding:utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import math as math

"""
根据gps采集的参考线数据，计算地图参考线需要的各个参数
"""
class CalcMapPara:
  ref_point_att_type = np.dtype([
    ('point',np.float16, (2,)),
    ('cuv',np.float16),
    ('grad_of_cuv', np.float16),
    ('width', np.float16, (2,)),
    ('distance', np.float32)
    ])

  def __init__(self, ref_line): # , ref_line_width
    self.ref_line = ref_line
    self.s_distance = 0
    self.cuv = 0
#    self.ref_line_width = ref_line_width
    self.ref_point_list = []

  def transRadianstoDegree(self, rad):
    return rad*180.0/math.pi

  def calcDistanceofTwoPoints(self, p1, p2):
    vect_l = np.array(p2) - np.array(p1)
    return np.sqrt(vect_l.dot(vect_l))

  # 曲率
  def calcCuv(self, p1, p2, p3): # 这个算法有问题
    ds = self.calcDistanceofTwoPoints(p1, p2)
    l12 = self.calcDistanceofTwoPoints(p1, p2)
    l23 = self.calcDistanceofTwoPoints(p2, p3)
    vect_p1p2 = np.array(p2) - np.array(p1)
    vect_p2p3 = np.array(p3) - np.array(p2)
    if l12 > 0 and l23 > 0:
      cos_angle = vect_p1p2.dot(vect_p2p3)/(l12*l23)
    else:
      return False
    angle = np.arctan(cos_angle)
    if ds > 0:
      return angle/ds
    else:
      return False

  # 曲率导数
  def calcGradeofCuv(self, cuv1, cuv2, delta_s):
    if delta_s > 0:
      return (cuv1-cuv2)/delta_s
    else:
      return False

  # 对整个ref_line参数进行计算
  def calcTotalLine(self):
    total_line = self.ref_line.tolist()
    point_cal_list = []

    ref_point_list = []
    cuv_list = []
    s_distance = 0

    for ind in range(len(total_line)):
      point_cal_list.append(total_line[ind])
      if ind>=2:
        cuv = self.calcCuv(total_line[ind-2], total_line[ind-1], total_line[ind-0]) # 这个地方有问题
        if not cuv:
          cuv = cuv_list[-1]
        cuv_list.append(cuv)
        if len(cuv_list)==2:
          gcuv = self.calcGradeofCuv(cuv_list[0], cuv_list[1], self.calcDistanceofTwoPoints(total_line[ind-3], total_line[ind-2]))
          if not gcuv:
            gcuv = 0
          ref_point = np.array(
            [(total_line[ind-3], 
              cuv_list[0], 
              gcuv, 
              (-1.5, 1.5), 
              s_distance)], 
            dtype = ref_point_att_type)
          s_distance = s_distance + self.calcDistanceofTwoPoints(total_line[ind-3], total_line[ind-2])
          ref_point_list.append(ref_point)
          cuv_list.pop(0)
        point_cal_list.pop(0)
    self.ref_point_list = ref_point_list

if __name__ == "__main__":
  ref_point_att_type = np.dtype([
    ('point',np.float16, (2,)),
    ('cuv',np.float16),
    ('grad_of_cuv', np.float16),
    ('width', np.float16, (2,)),
    ('distance', np.float32)
    ])
  
  direct = "../data/GPS_info/"
  filename = "xyz_b.txt.txt"

  file = open(direct+filename, 'r')
  try:
    total_line = np.loadtxt(file, delimiter='\t', usecols=[1,2])
  finally:
    file.close()
  scale = 1/0.116
  bias = [18.75, -0.75]
  total_line = (total_line - bias) * scale # 针对镇江地图的偏移

  fig = plt.figure('calc')
  ax = fig.add_subplot(111)
  print(total_line)
  x = total_line[:, 0]
  y = total_line[:, 1]
  ax.plot(x, y, 'o')
  plt.show()

  calc_map_para = CalcMapPara(total_line)
  calc_map_para.calcTotalLine()
  print(calc_map_para.ref_point_list[0])