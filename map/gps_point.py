import numpy as np


class GPSPoint():
    @classmethod
    def shiftPoint(cls, P0, size, scale, bias):
        p = np.array(P0)
        return tuple((p * size + bias) * scale)

    @classmethod
    def calcTwoPointsDistance(cls, P0, P1):
        return np.sqrt((P0[0] - P1[0])**2 + (P0[1] - P1[1])**2)
