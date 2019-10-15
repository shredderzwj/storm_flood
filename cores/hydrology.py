# -*- coding:utf-8 -*-
# 水文相关计算模块

import scipy.special
import scipy.stats


class PearsonThree(object):
    def __init__(self, cv, cs, avg=1):
        """
        P-III 曲线类
        参考文档：https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gamma.html
        :param cv: float 变差系数
        :param cs: float 偏态系数
        :param avg: float 均值（若单纯计算模比系数Kp，此项可不指定）
        """
        self.__set_param(cv, cs, avg)

    def __set_param(self, cv, cs, avg):
        """根据初始化数据进行参数设置"""
        self.avg = avg
        self.cv = cv
        self.cs = cs
        self.param = [cv, cs, avg]
        # gamma分布对象，基于 scipy.stats 包。
        self.distribution = self._get_distribution(cv, cs, avg)

    def set_param(self, cv, cs, avg):
        """重新进行参数设置,单个"""
        self.__set_param(cv, cs, avg)

    @staticmethod
    def _get_distribution(cv, cs, avg):
        shape = 4 / cs ** 2
        scale = avg * cv * cs / 2
        loc = avg * (1 - 2 * cv / cs)
        return scipy.stats.gamma(shape, loc, scale)

    @classmethod
    def _calc_kp(cls, p, cv, cs, avg):
        return cls._calc_q(p, cv, cs, avg) / avg

    @classmethod
    def _calc_q(cls, p, cv, cs, avg):
        return cls._get_distribution(cv, cs, avg).isf(p)

    def calc_q(self, p):
        """
        计算指定频率的洪水流量，也可以重新指定均值用于计算图集
        :param p: float 频率（注意是小数不是百分数）
        :return: float 流量
        """
        return self.distribution.isf(p)

    def calc_kp(self, p):
        """
        计算指定频率的模比系数 Kp 值。
        :param p:  float 频率（注意是小数不是百分数）
        :return: kp float 模比系数 Kp 值
        """
        return self.calc_q(p) / self.avg


if __name__ == '__main__':
    p3 = PearsonThree(0.5, 0.5*3.5, 100)
    print(p3.calc_kp(0.1))
