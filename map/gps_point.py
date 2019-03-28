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
        """
        计算有向线段中的点在法线方向上,是否在radius范围存在与tree的相交点:
        """
        angle_left = theta + np.pi / 2
        if angle_left > np.pi:
            angle_left = angle_left - 2 * np.pi
        elif angle_left < -np.pi:
            angle_left = angle_left + 2 * np.pi
        angle_left_diff = np.pi / 2

        angle_right = theta - np.pi / 2
        if angle_right > np.pi:
            angle_right = angle_right - 2 * np.pi
        elif angle_right < -np.pi:
            angle_right = angle_right + 2 * np.pi
        angle_right_diff = np.pi / 2
        # print('切线方向:{}, 法线方向:左:{}, 右:{}'.format(
        #     theta, angle_left * 180 / np.pi, angle_right * 180 / np.pi))

        left_width = 0
        right_width = 0
        left_point = []
        right_point = []

        points = tree.data[tree.query_ball_point(p, radius)]  # 在tree中寻找点
        if len(points) == 0:
            print('no points found')
            return [radius, radius], [[0, 0], [0, 0]]
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
            if angle_left_diff > 1 / radius:  # 实际没有找到左侧点, 这里也可以修改为 diff<(1/radius),因为我们的离散是按照1m执行的,最差的情况就是相距1m
                left_width = radius
                left_point = [0, 0]
            if angle_right_diff > 1 / radius:
                right_width = radius
                right_point = [0, 0]
            return [left_width, right_width], [left_point, right_point]


if __name__ == "__main__":
    ps = [0, 0]
    pe = [-1.73, -1]
    print(GPSPoint.getDiAngle(ps, pe) * 180 / np.pi)
