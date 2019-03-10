# -*- coding:utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import cv2
import os

"""
" 给出x，y（基于原点的坐标，以米为单位），和map
" 判断是否在map允许范围内：x、y取整后，map对应的位置为1,表示可选，并返回map所在位置的数据 or false
"""
def getRefPointByRelateXY(x, y, longi_map, lanti_map):
  intx = int(x);
  inty = int(y);
  if longi_map[intx, inty] or lanti_map[intx, inty]:
    return True
  else:
    return False

if __name__ == "__main__":
  direct = "../data/GPS_info/"
  coordi_type = "gps_"
  namelist = ['b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
#  namelist = ['b', 'c', 'd', 'e', 'f', 'g', 'i']

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

  """
  " 建立一个矩阵，大小为max_x + 5, max_y + 5 
  " 在x、y有值的地方赋值为gps ref point,并向外扩展2m，其他为零
  " 存储为grid_map.csv格式
  """
  x = xyz_map[:,1]
  y = xyz_map[:,0]
  max_x = max(x)
  min_x = min(x)
  max_y = max(y)
  min_y = min(y)
  print("max_x=", max_x, min_x, "max_y=", max_y, min_y)

  # 建立栅格地图存储空间
  grid_map_matrix = np.zeros((int(max_x)+5, int(max_y)+5), dtype=np.int8)
  
  # 定义一个gps数据类型
  gps_dtype = np.dtype([('longi',np.float64),('lanti', np.float64)])
  # 用于存储参考点的存储空间
  ref_point_matrix = np.zeros(grid_map_matrix.shape, dtype=gps_dtype)

  # 将gps分开存储为两个空间
  ref_point_longi = np.zeros(grid_map_matrix.shape)
  ref_point_lanti = np.zeros(grid_map_matrix.shape)

  # 开始存储
  for index in xyz_map:
    # 整数化
    intx = int(index[1])
    inty = int(index[0])
    # 栅格地图存储结构
    grid_map_matrix[intx, inty] = 1
    # 扩展参考点地图
    for px in range(-2,3):
      for py in range(-2,3):
        if intx+px >= 0 and inty+py >= 0:
          ref_point_matrix[intx+px, inty+py] = index;
          ref_point_longi[intx+px, inty+py] = index[1]
          ref_point_lanti[intx+px, inty+py] = index[0]
          continue

  """
  # 为了适应4N方法，将grid_map进行补齐
  """
  # 粗暴解决方法：当grid_map[i]==1，查找它周围的4斜向邻域是否为1,是，则将两者的横纵邻域设为2
  for x in range(grid_map_matrix.shape[0]):
    for y in range(grid_map_matrix.shape[1]):
      if grid_map_matrix[x,y]==1:
        if x+1<grid_map_matrix.shape[0] and y+1<grid_map_matrix.shape[1]:
          if grid_map_matrix[x+1, y+1] == 1:
            grid_map_matrix[x+1, y] = 2
            ref_point_matrix[x+1, y] = ref_point_matrix[x, y]
            ref_point_longi[x+1, y] = ref_point_longi[x, y]
            ref_point_lanti[x+1, y] = ref_point_lanti[x, y]
        if x-1>=0 and y-1>=0:
          if grid_map_matrix[x-1, y-1] == 1:
            grid_map_matrix[x-1, y] = 2
            ref_point_matrix[x-1, y] = ref_point_matrix[x, y]
            ref_point_longi[x-1, y] = ref_point_longi[x, y]
            ref_point_lanti[x-1, y] = ref_point_lanti[x, y]
        if x+1<grid_map_matrix.shape[0] and y-1>=0:
          if grid_map_matrix[x+1, y-1] == 1:
            grid_map_matrix[x+1, y] = 2
            ref_point_matrix[x+1, y] = ref_point_matrix[x, y]
            ref_point_longi[x+1, y] = ref_point_longi[x, y]
            ref_point_lanti[x+1, y] = ref_point_lanti[x, y]
        if x-1>=0 and y+1<grid_map_matrix.shape[1]:
          if grid_map_matrix[x-1, y+1] == 1:
            grid_map_matrix[x-1, y] = 2
            ref_point_matrix[x-1, y] = ref_point_matrix[x, y]
            ref_point_longi[x-1, y] = ref_point_longi[x, y]
            ref_point_lanti[x-1, y] = ref_point_lanti[x, y]
  # save data to file
  grid_map_matrix[grid_map_matrix==2] = 1
  grid_map_filename = direct + "grid_map" + ".csv"
  grid_map = np.savetxt(grid_map_filename, grid_map_matrix, fmt='%d', delimiter=',', newline='\n')
  
  longi_map_filename = direct + "longi_map" + ".csv"
  np.savetxt(longi_map_filename, ref_point_longi, fmt='%f', delimiter=',', newline='\n')

  lanti_map_filename = direct + "lanti_map" + ".csv"
  np.savetxt(lanti_map_filename, ref_point_lanti, fmt='%f', delimiter=',', newline='\n')

  """
  # 简单测试
  """
  print(getRefPointByRelateXY(23.3, 10.5, ref_point_longi, ref_point_lanti))

  # ref_point_file = open(ref_map_filename, 'rb')
  # try:
  #   ref_point = ref_point_file.read()
  #   pass
  # finally:
  #   ref_point_file.close()
  #   pass
  # print(ref_point)
