# -*- coding:utf-8 -*-

import numpy as np

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

def loadMap(direct):
    grid_file = direct + "grid_map.csv"
    longi_file = direct + "longi_map.csv"
    lanti_file = direct + "lanti_map.csv" 
    try:
      grid_map = np.loadtxt(grid_file, delimiter=',')
      longi_map = np.loadtxt(longi_file, delimiter=',')
      lanti_map = np.loadtxt(lanti_file, delimiter=',')
    except IOError:
      print("file open failed")
      return False    
    return (grid_map, longi_map, lanti_map)

if __name__ == "__main__":
    direct = "../data/GPS_info/"

    (grid_map, longi_map, lanti_map) = loadMap(direct)
    
    print(getRefPointByRelateXY(23.3, 10.5, longi_map, lanti_map))