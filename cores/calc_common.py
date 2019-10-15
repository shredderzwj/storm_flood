# -*- coding:utf-8 -*-

import numpy as np
from .hydrology import PearsonThree


def calc_kps(ps, cvs, css):
    """
    计算各设计频率下的模比系数 Kp
    :param ps: iterable object -> floats 需要计算的频率
    :param cvs: iterable object -> floats 各历时变差系数
    :param css: iterable object -> floats 各历时偏态系数
    :return: len(ps) * len(cvs)D 矩阵 floats
    """
    return np.array([[PearsonThree(cv, css[i]).calc_kp(p) for i, cv in enumerate(cvs)] for p in ps])


def calc_design_point_rainfalls(ps, cvs, css, point_rainfalls):
    """
    计算各历时、各设计频率的设计点雨量
    计算各历时、各设计频率的设计面雨量
    :param ps: iterable object -> floats 需要计算的频率
    :param point_rainfalls: iterable object -> floats 各历时点雨量， 本项目中统一分为 10min, 1h, 6h, 24h
    :param cvs: iterable object -> floats 各历时变差系数
    :param css: iterable object -> floats 各历时偏态系数
    :return: len(ps) * len(point_rainfalls)D 矩阵 floats
    """
    kps = calc_kps(ps, cvs, css)
    return np.array([kp * np.array(point_rainfalls) for kp in kps])


def calc_design_area_rainfalls(ps, cvs, css, point_rainfalls, alphas):
    """
    计算各历时、各设计频率的设计面雨量
    :param ps: iterable object -> floats 需要计算的频率
    :param point_rainfalls: iterable object -> floats 各历时点雨量， 本项目中统一分为 10min, 1h, 6h, 24h
    :param cvs: iterable object -> floats 各历时变差系数
    :param css: iterable object -> floats 各历时偏态系数
    :param alphas:  iterable object -> floats 各历时点面折减系数, 维度同点雨量
    :return: len(ps) * len(point_rainfalls)D 矩阵 floats
        """
    design_point_rainfalls = calc_design_point_rainfalls(ps, cvs, css, point_rainfalls)
    return np.array([x * alphas[i] for i, x in enumerate(design_point_rainfalls.T)]).T


def calc_ns(h10minp_area_rainfalls, h1hp_area_rainfalls, h6hp_area_rainfalls, h24hp_area_rainfalls):
    """
    计算暴雨递减指数 n
    :param h10minp_area_rainfalls: iterable object -> 各设计频率下的10min历时设计面雨量
    :param h1hp_area_rainfalls: iterable object -> 各设计频率下的1h历时设计面雨量
    :param h6hp_area_rainfalls: iterable object -> 各设计频率下的6h历时设计面雨量
    :param h24hp_area_rainfalls: iterable object -> 各设计频率下的24h历时设计面雨量
    :return: len(h10minp_area_rainfalls) * 3 矩阵 float  每一维分别为 各设计频率下的 n1, n2, n3
    """
    if not len(h10minp_area_rainfalls) == len(h1hp_area_rainfalls) == len(h6hp_area_rainfalls) == len(h24hp_area_rainfalls):
        raise ReferenceError('各参数长度不一致')
    h10minp_area_rainfalls = np.array(h10minp_area_rainfalls)
    h1hp_area_rainfalls = np.array(h1hp_area_rainfalls)
    h6hp_area_rainfalls = np.array(h6hp_area_rainfalls)
    h24hp_area_rainfalls = np.array(h24hp_area_rainfalls)
    n1s = 1 - 1.285 * np.log10(h1hp_area_rainfalls / h10minp_area_rainfalls)
    n2s = 1 - 1.285 * np.log10(h6hp_area_rainfalls / h1hp_area_rainfalls)
    n3s = 1 - 1.661 * np.log10(h24hp_area_rainfalls / h6hp_area_rainfalls)
    return np.array([n1s, n2s, n3s]).T


def calc_r_24h_allocate(r24ps, n2ps, n3ps, h6ps, h24ps):
    """
    计算24小时净雨概化时程分配
    :param r24ps: iterable object -> float  各设计频率24h净雨量
    :param n2ps: iterable object -> float 各设计频率1~6h暴雨递减指数n2
    :param n3ps: iterable object -> float 各设计频率6~24h暴雨递减指数n3
    :param h6ps: iterable object -> float 各设计频率年最大6小时雨量
    :param h24ps: iterable object -> float 各设计频率年最大24小时雨量
    :return: len(n2ps) * 24D matrix -> float 24h各小时时程分配量
    """
    scale_factor_base = [
        {12: 10, 13: 12, 14: 16, 15: 38, 16: 14, 17: 10},
        {12: 8, 13: 10, 14: 16, 15: 44, 16: 12, 17: 10},
        {12: 7, 13: 7, 14: 15, 15: 54, 16: 10, 17: 7},
        {12: 5, 13: 6, 14: 12, 15: 64, 16: 8, 17: 5},
        {5: 4, 6: 5, 7: 6, 8: 8, 9: 8, 10: 10, 11: 10, 18: 10, 19: 8, 20: 8, 21: 6, 22: 6, 23: 6, 24: 5},
        {7: 6, 8: 6, 9: 9, 10: 10, 11: 10, 18: 14, 19: 10, 20: 9, 21: 7, 22: 7, 23: 6, 24: 6},
        {8: 6, 9: 10, 10: 12, 11: 12, 18: 16, 19: 12, 20: 10, 21: 10, 22: 6, 23: 6},
    ]

    scale_factor = np.zeros((len(scale_factor_base), 24))
    for i, row in enumerate(scale_factor_base):
        for k, v in row.items():
            scale_factor[i][k - 1] = v / 100
    h6ps = np.array([np.full(24, x) for x in h6ps])
    h24ps = np.array([np.full(24, x) for x in h24ps])
    r24ps = np.array([np.full(24, x) for x in r24ps])
    r6ps = h6ps / h24ps * r24ps
    scale_factor_r6 = np.zeros((len(n2ps), 24))
    scale_factor_r24 = np.zeros((len(n2ps), 24))
    for i, row in enumerate(n2ps):
        if 0.4 <= row < 0.5:
            scale_factor_r6[i] = scale_factor[0]
        elif 0.5 <= row < 0.6:
            scale_factor_r6[i] = scale_factor[1]
        elif 0.6 <= row < 0.7:
            scale_factor_r6[i] = scale_factor[2]
        else:
            scale_factor_r6[i] = scale_factor[3]

        if n3ps[i] < 0.6:
            scale_factor_r24[i] = scale_factor[4]
        elif 0.6 <= n3ps[i] < 0.7:
            scale_factor_r24[i] = scale_factor[5]
        else:
            scale_factor_r24[i] = scale_factor[6]
    r6_result = r6ps * scale_factor_r6
    r24_result = (r24ps - r6ps) * scale_factor_r24
    result = np.array([[r24_result[i][j] or col for j, col in enumerate(r6_result[i])] for i, row in enumerate(r6_result)])
    return result


# def calc_taus(l, m, j, qs):
#     """
#     计算汇流时间 τ
#     :param l: float 干流长度，设计断面至分水岭（公里）
#     :param j: float l 的平均比降
#     :param m: float 汇流参数 查图 θ~m曲线
#     :param qs: iterable object -> float 各频率流量
#     :return: len(qs)D vector 各频率汇流时间
#     """
#     return np.array([0.278 * l / (m * j**(1/3) * q**0.25) for q in qs])
#
#
# def calc_psi(f, l, j, m, mu, ss, n2s, n3s):
#     qs = calc_qs(f, l, j, m, mu, ss, n2s, n3s)
#     tau = calc_taus(l, m, j, qs)
#     if tau <= 1:
#         n = n2s
#     else:
#         n = n3s
#     psi = 1 - mu * tau ** n / ss
#     return psi


def calc_qs(f, l, j, m, mu, ss, n2s, n3s):
    """
    推理公式法计算洪峰流量
    :param f: float 流域面积（平方公里）
    :param l: float 干流长度，设计断面至分水岭（公里）
    :param j: float l 的平均比降
    :param m: float 汇流参数 查图 θ~m曲线
    :param mu: 平均入渗率，（mm/h）
    :param ss: iterable object -> float 各设计频率最大1h雨量平均强度，即设计频率1h雨量（mm/h）
    :param n2s: iterable object -> float 各设计频率1~6h暴雨递减指数n2
    :param n3s: iterable object -> float 各设计频率6~24h暴雨递减指数n3
    :return: len(ss)D vector -> float 个设计频率洪峰流量
    """
    qms = np.ones(len(ss))
    taus = np.ones(len(ss))
    psis  = np.ones(len(ss))
    ns = np.ones(len(ss))
    for i, s in enumerate(ss):
        n2 = n2s[i]
        n3 = n3s[i]
        q = qms[i]
        qm = 1e20
        while np.abs(q - qm) > 1e-4:
            q = qm
            tau = 0.278 * l / (m * j**0.33333333 * q**0.25)
            if tau <= 1:
                n = n2
            else:
                n = n3
            psi = 1 - mu * tau**n / s
            qm = 0.278 * psi * s * f / tau**n
        if qm < 0:
            qm = 0.0
            psi = 0.0
        qms[i] = qm
        taus[i] = tau
        psis[i] = psi
        ns[i] = n
    return np.array([qms, taus, psis, ns]).T


def calc_per_hour_hps(h1ps, h24ps, n2s, n3s):
    """
    计算1~24h各时段雨量，主要用于计算时程分配
    :param h1ps: iterable object -> float 各设计频率1h历时点雨量
    :param h24ps: iterable object -> float 各设计频率24h历时点雨量
    :param n2s: iterable object -> float 各设计频率n2
    :param n3s: iterable object -> float 各设计频率n3
    :return: len(h1p) * 24 matrix
    """
    h1ps = np.array(h1ps)
    h24ps = np.array(h24ps)
    n2s = np.array(n2s)
    n3s = np.array(n3s)
    per_hour_hps = []
    for i in range(24):
        t = i + 1
        if t < 6:
            per_hour_hps.append(h1ps * t**(1 - n2s))
        else:
            per_hour_hps.append(h24ps * 24**(n3s - 1) * t**(1 - n3s))
    return np.array(per_hour_hps).T


def calc_hps_allocate(h1ps, h24ps, n2s, n3s):
    """
    24小时暴雨时程分配，逐时降雨量
    :param h1ps: iterable object -> float 各设计频率1h历时点雨量
    :param h24ps: iterable object -> float 各设计频率24h历时点雨量
    :param n2s: iterable object -> float 各设计频率n2
    :param n3s: iterable object -> float 各设计频率n3
    :return: len(per_hour_hps)*24 matrix 各设计频率逐时降雨量
    """
    per_hour_hps = np.array(calc_per_hour_hps(h1ps, h24ps, n2s, n3s)).T
    allocate = []
    # h24ps = np.array([sum(per_hour_hp) for per_hour_hp in per_hour_hps])
    for i in range(6):
        allocate.append(1 / 6 * (per_hour_hps[23] - per_hour_hps[17]))
    allocate.append(per_hour_hps[15] - per_hour_hps[14])
    allocate.append(per_hour_hps[13] - per_hour_hps[12])
    allocate.append(per_hour_hps[11] - per_hour_hps[10])
    allocate.append(per_hour_hps[9] - per_hour_hps[8])
    allocate.append(per_hour_hps[7] - per_hour_hps[6])
    allocate.append(per_hour_hps[5] - per_hour_hps[4])
    allocate.append(per_hour_hps[3] - per_hour_hps[2])
    allocate.append(per_hour_hps[1] - per_hour_hps[0])
    allocate.append(per_hour_hps[0])
    allocate.append(per_hour_hps[2] - per_hour_hps[1])
    allocate.append(per_hour_hps[4] - per_hour_hps[3])
    allocate.append(per_hour_hps[6] - per_hour_hps[5])
    allocate.append(per_hour_hps[8] - per_hour_hps[7])
    allocate.append(per_hour_hps[10] - per_hour_hps[9])
    allocate.append(per_hour_hps[12] - per_hour_hps[11])
    allocate.append(per_hour_hps[14] - per_hour_hps[13])
    allocate.append(per_hour_hps[16] - per_hour_hps[15])
    allocate.append(per_hour_hps[17] - per_hour_hps[16])
    return np.array(allocate).T


def calc_per_hour_rps(r24ps, h1ps, h24ps, n2s, n3s, mu):
    """
    计算诸时净雨
    :param r24ps:iterable object -> float 各设计频率24h静雨
    :param h1ps: iterable object -> float 各设计频率1h历时点雨量
    :param h24ps: iterable object -> float 各设计频率24h历时点雨量
    :param n2s: iterable object -> float 各设计频率n2
    :param n3s: iterable object -> float 各设计频率n3
    :param mu: float 平均入渗率
    :return:  逐时净雨
    """
    hps_allocate = np.array(calc_hps_allocate(h1ps, h24ps, n2s, n3s))

    # 计算静雨比例
    rs_allocate = np.array([(hps - mu) for i, hps in enumerate(hps_allocate.T)])
    rs_allocate[rs_allocate < 0] = 0.0
    rs_allocate = np.array([hps / sum(hps) for i, hps in enumerate(rs_allocate.T)]).T
    rs_allocate = np.array([hps * r24ps for i, hps in enumerate(rs_allocate)])
    return rs_allocate.T
    

def calc_qs_allocate(f, l, j, m, mu, ss, n2s, n3s, per_hour_rps):
    """
    计算洪水过程线
    :param f: float 流域面积（平方公里）
    :param l: float 干流长度，设计断面至分水岭（公里）
    :param j: float l 的平均比降
    :param m: float 汇流参数 查图 θ~m曲线
    :param mu: 平均入渗率，（mm/h）
    :param ss: iterable object -> float 各设计频率最大1h雨量平均强度，即设计频率1h雨量（mm/h）
    :param n2s: iterable object -> float 各设计频率1~6h暴雨递减指数n2
    :param n3s: iterable object -> float 各设计频率6~24h暴雨递减指数n3
    :param f: float 流域面积
    :return: len(per_hour_rps)*24 matrix 各设计频率洪水工程
    """
    # qs = calc_qs(f, l, j, m, mu, ss, n2s, n3s)
    # psi = calc_qs(f, l, j, m, mu, ss, n2s, n3s)
    # taus = calc_taus(l, m, j, qs)
    # rps = np.array(per_hour_rps)
    # qs = [0.278 * rs * f / taus for rs in rps.T]
    # return np.array(qs).T
    pass

