import numpy as np


class GPSPoint():
    @classmethod
    def shiftPoint(cls, P0, size, scale, bias):
        p = np.array(P0)
        return tuple((p * size + bias) * scale)

    @classmethod
    def calcTwoPointsDistance(cls, P0, P1):
        return np.sqrt((P0[0] - P1[0])**2 + (P0[1] - P1[1])**2)

    @classmethod
    def getDiAngle(cls, Ps, Pe):
        """
        计算有向线段的与x轴的夹角:
            实际可以认为是Ps-Pe构成的有向线段与x轴单位向量的夹角
        """
        angle = 0
        start = np.array(Ps)
        end = np.array(Pe)
        pline = end - start
        l = GPSPoint.calcTwoPointsDistance(Ps, Pe)
        pline = pline / l
        angle = np.arccos(np.dot([1, 0], pline))
        if angle >= 0 and pline[1] < 0:
            angle = -1 * angle
        return angle

    @classmethod
    def getWidthinP(cls, p, radius, theta, tree):
        points = tree.data[tree.query_ball_point(p, radius)]
        angle_left = theta + np.pi / 2
        angle_left_diff = np.pi / 2
        angle_right = theta - np.pi / 2
        angle_right_diff = np.pi / 2
        left_width = 0
        right_width = 0
        left_point = []
        right_point = []
        if len(points) == 0:
            print('no points found')
            return [radius, radius], [0, 0]
        else:
            for pe in points:
                angle = GPSPoint.getDiAngle(p, pe)
                if np.abs(angle - angle_left) <= angle_left_diff:
                    angle_left_diff = np.abs(angle - angle_left)
                    left_width = GPSPoint.calcTwoPointsDistance(p, pe)
                    left_point = pe
                if np.abs(angle - angle_right) <= angle_right_diff:
                    angle_right_diff = np.abs(angle - angle_right)
                    right_width = GPSPoint.calcTwoPointsDistance(p, pe)
                    right_point = pe
            print('ducing:{}'.format([[left_width, right_width],
                                      [angle_left, angle_right],
                                      [left_point, right_point]]))
            if angle_left_diff >= np.pi / 2:  # 实际没有找到左侧点
                left_width = radius
                left_point = []
            if angle_right_diff >= np.pi / 2:
                right_width = radius
                right_point = []
            return [left_width, right_width], [left_point, right_point]


if __name__ == "__main__":
    pass
