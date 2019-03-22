# -*- coding : utf-8

# 用于实现json文件的存储与读取
import json
import numpy as np


class LineEntity:
    def __init__(self,
                 linetype='LINE',
                 start=[],
                 end=[],
                 angle=[],
                 center=[],
                 radius=0):
        self.linetype = linetype
        self.start = list(start)
        self.end = list(end)
        self.angle = list(angle)
        self.center = list(center)
        self.radius = radius


class RefPointPara:
    """
  参考点属性结构体
  """

    def __init__(self,
                 point=[0.0, 0.0],
                 width=[2, 2],
                 cuv=0,
                 gcuv=0,
                 s=0,
                 theta=0):
        self.point = point
        self.width = width
        self.cuv = cuv
        self.gcuv = gcuv
        self.s = s
        self.theta = theta

    def calcDistance(self, p1, p2):
        distance = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
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


class LineEntityEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, LineEntity):
            return (obj.linetype, obj.start, obj.end, obj.angle, obj.center,
                    obj.radius)
        return json.JSONEncoder.default(self, obj)


class RefPointParaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, RefPointPara):
            # return [
            #     'p', obj.point, 's', obj.s, 'w', obj.width, 'theta', obj.theta,
            #     'cuv', obj.cuv, 'gcuv', obj.gcuv
            # ]
            return (obj.point, obj.s, obj.width, obj.theta, obj.cuv, obj.gcuv)
        return json.JSONEncoder.default(self, obj)


class ConnectMap:
    def __init__(self,
                 end_point=[],
                 ref_line_id=0,
                 ref_line_length=0,
                 speed_limited=-1):
        self.end_point = end_point
        self.ref_line_id = ref_line_id
        self.ref_line_length = ref_line_length
        self.speed_limited = speed_limited

    def setSpeedLimited(self, speed_limited):
        self.speed_limited = speed_limited


class ConnectMapKey:
    def __init__(self, start_point=[]):
        self.start_point = start_point


class ConnectMapEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ConnectMap):
            # return [
            #     'p', obj.point, 's', obj.s, 'w', obj.width, 'theta', obj.theta,
            #     'cuv', obj.cuv, 'gcuv', obj.gcuv
            # ]
            return (obj.end_point, obj.ref_line_id, obj.ref_line_length,
                    obj.speed_limited)

        elif isinstance(obj, ConnectMapKey):
            return (obj.start_point)

        return json.JSONEncoder.default(self, obj)


def saveJsonFile(file, wt, dicts, encoder):
    pass
    pf = open(file, wt)
    obj = json.dumps(dicts, cls=encoder)
    pf.write(obj)
    pf.close()


def saveConnectMapToJson(file, wt, dicts):
    pass
    saveJsonFile(file, wt, dicts, ConnectMapEncoder)


def saveLineMapToJson(file, wt, dicts):
    pass
    saveJsonFile(file, wt, dicts, LineEntityEncoder)


def saveRefPointParaDictToJson(file, wt, dicts):
    pass
    saveJsonFile(file, wt, dicts, RefPointParaEncoder)
    # pf = open(file, wt)
    # pf.writelines("value = point, s, width, theta, cuv, gcuv\n")
    # for item in dicts.items():
    #     obj = json.dumps(item, cls=RefPointParaEncoder, separators=(',', ':'))
    #     pf.writelines(obj)
    #     pf.writelines("\n")
    # pf.close()


def readFromJson(filename, decoder):
    try:
        pf = open(filename)
        data = pf.read()
        obj = json.loads(data, encoding=decoder)
    except FileNotFoundError:
        return False
    pf.close()
    return obj


def readRefPointParaDictFromJson(filename):
    pass
    return readFromJson(filename, RefPointParaEncoder)


def initLineEntryFromJsonObj(JsonObj):
    entity = LineEntity(JsonObj[0], JsonObj[1], JsonObj[2], JsonObj[3],
                        JsonObj[4], JsonObj[5])

    return entity


def getLineEntryDictFromJsonObj(line_map_obj):
    line_entities_dict = {}
    # read data from file
    for _, key in enumerate(line_map_obj):
        if key == 0:
            print("main: {}:{}".format(key, line_map_obj[key][0]))
        entity = initLineEntryFromJsonObj(line_map_obj[key])
        line_entities_dict[key] = entity
    return line_entities_dict


def readConnectMapFromJson(filename):
    pass
    return readFromJson(filename, ConnectMapEncoder)


def readLineMapFromJson(filename):
    pass
    return readFromJson(filename, LineEntityEncoder)


if __name__ == "__main__":
    obj = readConnectMapFromJson('connect_map.json')
    print(len(obj))
    for _, key in enumerate(obj):
        print('{}:{}'.format(key, obj[key]))
