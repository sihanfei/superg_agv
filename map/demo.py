# # -*- coding:utf-8 -*-

# # import numpy as np
# # # import matplotlib.pyplot as plt
# # # import scipy.spatial as spt
# # # import matplotlib.image as mpimg
# # # import PIL.Image as PIImg


# # # class ModifyMap:
# # #   def __init__(self, fig, gps_map):
# # #     self.map_tree = spt.KDTree(gps_map)
# # #     self.total_line = gps_map
# # #     self.line_list = gps_map.tolist()
# # #     self.fig = fig

# # #   def onPick(self, event):
# # #     mousevent = event.mouseevent
# # #     thisline = event.artist
# # #     xdata = thisline.get_xdata()
# # #     ydata = thisline.get_ydata()
# # #     ind = event.ind
# # #     points = tuple(zip(xdata[ind], ydata[ind]))
# # #     point = points[0]
# # #     position = np.where(self.total_line == point)
# # #     self.drawPoint(point)
# # #     print(position)
# # #     point = self.total_line[zip(position)]
# # #     self.drawPoint(point)


# # #   def callBackConnect(self):
# # #     self.fig.canvas.mpl_connect('pick_event', self.onPick)
# # #     return

# # #   def callBackDisconnect(self):
# # #     self.fig.canvas.mpl_disconnect(self.onPick)
# # #     return

# # #   def drawPoint(self, road_point):
# # #     # add the point/ID/annotate
# # #     plt.plot(road_point[0], road_point[1], 'r.')
# # #     self.fig.canvas.draw()




# # # # dt = np.dtype([
# # # #   ('name', np.unicode_, 16), 
# # # #   ('grades', np.float64, (2,))
# # # #   ])
# # # # x = np.array([('Sarah', (8.0, 7.0))], dtype=dt)
# # # # print(x)

# # # # demo_type = np.dtype([
# # # #   ('point', np.float16, (2,)),
# # # #   ('width', np.float16, (2,))
# # # #   ])
# # # # print(demo_type['point'])
# # # # demo_list = []
# # # # demo_data = np.array(
# # # #   [(
# # # #     (1.0, 2.0),
# # # #     (1.5, 1.5)
# # # #   )], dtype = demo_type)
# # # # demo_list.append(demo_data)
# # # # print(demo_list)

# # # # forlist = [
# # # #     (1.0, 2.0),
# # # #     (1.5, 1.5),
# # # #     (1.8, 2.5),
# # # #     (2.2, 2.0),
# # # #     (1.8, 2.0)
# # # #   ]
# # # # print(forlist)
# # # # forlist.sort()
# # # # print(forlist)
# # # if __name__ == "__main__":
# # #   direct = "../data/GPS_info/"
# # #   filename = "map_point_data.csv"

# # #   xyz_map = np.loadtxt(direct+filename, delimiter=',')
# # #   img1 = PIImg.open(direct+"zhenjiang.bmp")
# # #   npimg1 = np.array(img1)
# # #   npimg1 = npimg1[-1:0:-1,:,:]
# # #   scale = 1/0.116
# # #   bias = [18.75, -0.75]
# # #   xyz_map = (xyz_map-bias)*scale # 针对镇江地图的偏移

# # #   # 准备绘图
# # #   x = xyz_map[:, 0]
# # #   y = xyz_map[:, 1] 
# # #   fig = plt.figure()
# # #   ax = fig.add_subplot(111)
# # #   ax.set_title('modify map')
# # #   ax.plot(x, y, 'g.', picker = 5)

# # #   # 显示并关联到选点程序
# # #   ax.imshow(npimg1, origin = 'lower')
# # #   ax.autoscale(False)
# # #   # map_modi = ModifyMap(fig, xyz_map, annt_dict, point_dict)
# # #   # map_modi.callBackConnect()
# # #   modify_map = ModifyMap(fig, xyz_map)
# # #   modify_map.callBackConnect()
# # #   plt.show()

# # a=np.array([
# #   [1.0, 2.0],
# #   [1.0, 2.33],
# #   [1.0, 2.33],
# #   [3.0, 2.33]
# #   ])

# # print(np.unique(a, axis=0))

# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.lines as lines
# import matplotlib.transforms as mtransforms
# import matplotlib.text as mtext


# class MyLine(lines.Line2D):
#     def __init__(self, *args, **kwargs):
#         # we'll update the position when the line data is set
#         self.text = mtext.Text(0, 0, '')
#         lines.Line2D.__init__(self, *args, **kwargs)

#         # we can't access the label attr until *after* the line is
#         # inited
#         self.text.set_text(self.get_label())

#     def set_figure(self, figure):
#         self.text.set_figure(figure)
#         lines.Line2D.set_figure(self, figure)

#     def set_axes(self, axes):
#         self.text.set_axes(axes)
#         lines.Line2D.set_axes(self, axes)

#     def set_transform(self, transform):
#         # 2 pixel offset
#         texttrans = transform + mtransforms.Affine2D().translate(2, 2)
#         self.text.set_transform(texttrans)
#         lines.Line2D.set_transform(self, transform)

#     def set_data(self, x, y):
#         if len(x):
#             self.text.set_position((x[-1], y[-1]))

#         lines.Line2D.set_data(self, x, y)

#     def draw(self, renderer):
#         # draw my label at the end of the line with 2 pixel offset
#         lines.Line2D.draw(self, renderer)
#         self.text.draw(renderer)

# # Fixing random state for reproducibility
# np.random.seed(19680801)


# fig, ax = plt.subplots()
# x, y = np.random.rand(2, 20)
# line = MyLine(x, y, mfc='red', ms=12)
# #line.text.set_text('line label')
# line.text.set_color('red')
# line.text.set_fontsize(16)


# ax.add_line(line)


# plt.show()

from scipy import spatial
import numpy as np
import matplotlib.pyplot as plt

a=np.array([2.0, 1.0])
b=np.array([4.0, 2.0])
print((a+b)/2)
