import numpy as np
from gps_point import GPSPoint as gp
import JsonFormat as jft
import matplotlib.pyplot as plt
import PIL.Image as PIImg


class EntityOfMap():  # dxf中实体对象
    def __init__(self):
        return

    # 将dxf中的mm转换为m, 并根据图片的缩放\平移需求,对entity进行参数的重置
    def DXFEntityReinit(self, orig_DXF_entity, scale, bias):
        if orig_DXF_entity.dxftype == 'LINE':
            orig_DXF_entity.start = gp.shiftPoint(orig_DXF_entity.start,
                                                  1 / 1000, scale, bias)
            orig_DXF_entity.end = gp.shiftPoint(orig_DXF_entity.end, 1 / 1000,
                                                scale, bias)
        elif orig_DXF_entity.dxftype == 'ARC':
            orig_DXF_entity.center = gp.shiftPoint(orig_DXF_entity.center,
                                                   1 / 1000, scale, bias)
            orig_DXF_entity.radius = orig_DXF_entity.radius / 1000
            orig_DXF_entity.start_angle = orig_DXF_entity.start_angle * np.pi / 180
            orig_DXF_entity.end_angle = orig_DXF_entity.end_angle * np.pi / 180
            if orig_DXF_entity.start_angle > orig_DXF_entity.end_angle:  # 为防止画图出错,强制让start小于end
                orig_DXF_entity.start_angle = orig_DXF_entity.start_angle - 2 * np.pi

    # 将dxfentity转换为lineentity
    def changeDXFEntityToLineEntity(self, DXFEntity):
        line_entity = jft.LineEntity()
        return line_entity

    # 根据lineentity参数,计算离散点GPS坐标
    def makeGPSPointsFromLineEntity(self, LineEntity):
        points = []
        return points

    # 根据dxfentity参数,计算entity的线段/弧线长度
    def getLineEntityLength(self, DXFEntity):
        return

    # 根据
    def drawLineEntity(self, LineEntity, ax=None, **kwds):
        if ax is None:
            cf = plt.gcf()
        else:
            cf = ax.get_figure()
        cf.set_facecolor('w')
        if ax is None:
            if cf._axstack() is None:
                ax = cf.add_axes((0, 0, 1, 1))
            else:
                ax = cf.gca()
        points = self.makeGPSPointsFromLineEntity(LineEntity)
        x = []
        y = []
        for point in points:
            x.append(point[0])
            y.append(point[1])
        if ax is None:
            plt.plot(x, y, **kwds)
        else:
            ax.plot(x, y, **kwds)


if __name__ == "__main__":
    img1 = PIImg.open(../data/map/zhenjiang/zhenjiang.bmp)
    npimg1 = np.array(img1)
    npimg1 = npimg1[-1:0:-1, :, :]
    scale = 1 / 0.116
    bias = [18.75, -0.75]
    # xyz_map = (xyz_map - bias) * scale  # 针对镇江地图的偏移

    # 准备绘图
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # 读取dxf文件
    dxf_object = grb.readfile(in_dxf_file)
    