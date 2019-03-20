# -*- coding : utf-8

# 用于实现json文件的存储与读取
import json
import numpy as np

class RefPointPara:
  """
  参考点属性结构体
  """
  def __init__(self, point=[0.0, 0.0], width=[2,2], cuv=0, gcuv=0, s=0, theta=0):
    self.point = point
    self.width = width
    self.cuv = cuv
    self.gcuv = gcuv
    self.s = s
    self.theta = theta
  
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

  def setTheta(self, theta):
    self.theta = theta

  def getWidth(self):
    return self.width
  
  def getTheta(self):
    return self.theta
  
  def getS(self):
    return self.s

  def getPoint(self):
    return self.point

  def getCuv(self):
    return self.cuv
  
  def getGcuv(self):
    return self.gcuv


class RefPointParaEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, RefPointPara):
      return ['p', obj.point, 's', obj.s, 'w', obj.width, 'theta', obj.theta, 'cuv', obj.cuv, 'gcuv', obj.gcuv]
        # Let the base class default method raise the TypeError
    return json.JSONEncoder.default(self, obj)

def saveJsonFile(file, wt, dicts, encoder):
  pass
  pf = open(file, wt)
  obj = json.dumps(dicts, cls=encoder)
  pf.write(obj)
  pf.close()

def saveRefPointParaDictToJson(file, wt, dicts):
  pass
  pf = open(file, wt)
  for index, _ in enumerate(dicts):
    print(dicts[index])
    obj = json.dumps(dicts[index], cls=RefPointParaEncoder)
    pf.writeline(obj)
  pf.close()


if __name__ == "__main__":
  demo_list = []
  for i in range(10):
    p = RefPointPara([i, i**2], [2,2], 0, 0, i**3)
    demo_list.append(p)
  a_dict = {'key':demo_list, 'k2':demo_list}
  # saveRefPointParaDictToJson('demo.json', 'w', a_dict)
  a_dict(0)

