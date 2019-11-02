# -*- coding:utf-8 -*-

import numpy as np

from .db_info import contour, area, relationship, area_info, contour_info
from .conf import proj
from .topology import quadrant8, is_in_area


def get_area(lon, lat):
    for k, v in area.items():
        if is_in_area((lon, lat), v):
            return k


def get_distance(p1, p2):
    p1 = np.array(p1)
    p2 = np.array(p2)
    return np.sqrt(np.sum((p1 - p2)**2))


def get_contour_value(key, point_coord):
    """
    查等值线图
    :param key: int 图编号
    :param point_coord:  (float, float) 点的经纬度坐标
    :return:  float 值
    """
    # 八分坐标系，在每个象限找到与已知点的最短距离
    min_distance_points = {}
    min_distance = {}
    for i in range(8):
        min_distance[i + 1] = 1e20
    point_coord = proj(*point_coord)
    infos = contour.get(key)
    for info in infos:
        point_contour = info[:-1]
        quadrant = quadrant8(point_coord, point_contour)
        distance = get_distance(point_coord, point_contour)
        if distance < min_distance[quadrant]:
            min_distance_points[quadrant] = info
            min_distance[quadrant] = distance

    # !对求得的每个象限最近距离差值加权平均计算得读取数值。
    qz = 0
    sum_zqz = 0
    for k, v in min_distance_points.items():
        qz += 1 / min_distance[k] ** 2
        sum_zqz += 1 / min_distance[k] ** 2 * v[-1]

    if qz == 0:
        return 0
    return sum_zqz / qz


def get_relationship_value(key, x):
    """
    查关系曲线图
    :param key: int 查图代码 见 db_info模块
    :param x: float 已知x值
    :return: floay 根据关系曲线查的 y 值
    """
    relationship_curve = sorted(relationship.get(key), key=lambda x: x[0])
    xs, ys = zip(*relationship_curve)
    if x in xs:
        return ys[xs.index(x)]

    if x < xs[0]:
        return ys[0]

    if x > xs[-1]:
        return ys[-1]

    for i, x_in_xs in enumerate(xs[:-1]):
        if x_in_xs < x < xs[i + 1]:
            x1 = x_in_xs
            x2 = xs[i + 1]
            y1 = ys[i]
            y2 = ys[i + 1]
            return (x-x1)*(y2-y1)/(x2-x1)+y1


def get_chart(lon, lat):
    """
    查算选定位置所在的分区及各暴雨参数
    :param lon: float 经度
    :param lat: float 纬度
    :return: dict 查图结果，封装为字典，结构如下： （若输入的坐标不在计算范围，返回空字典）
            {
                'area': int 分区代码
                'area_name': str 分区名
                'contours': [
                    {
                        'key': int 等值线图的代码,
                        'name': str 等值线图名，
                        'var': str 等值线变量名，
                        'value': float 值,
                    },
                    ……
                ],  # 各等值线查图结果信息
            }
    """
    area_key = get_area(lon, lat)   # 图编号 见 db_info模块
    if not area_key:
        return {}
    contour_values = {}
    for key in contour_info.keys():
        contour_values[key] = get_contour_value(key, (lon, lat))
    return {
        'area': area_key,    # 分区代码
        'area_name': area_info[area_key],    # 分区名
        'contours': [{"key": k, "name": v[0], "var": v[1], "value": contour_values[k]} for k, v in contour_info.items()],
    }


def get_alphas(area, f):
    """
    查 t-f-α 时面深关系图，获取点面折减系数α
    :param area: int 分区代码
    :param f float 流域面积
    :return: 4D tuple 各历时点面折减系数 (float, float, float, float)
            历时分别为(10min, 1h, 6h, 24h)
    """
    if f <= 50:
        return 1, 1, 1, 1
    if area == 1:
        key = 1
    elif area in [2, 3, 4]:
        key = 2
    else:
        key = 3
    alpha_10min = get_relationship_value(8424100 + key, f)
    alpha_1h = get_relationship_value(8424010 + key, f)
    alpha_6h = get_relationship_value(8424060 + key, f)
    alpha_24h = get_relationship_value(8424240 + key, f)
    return alpha_10min, alpha_1h, alpha_6h, alpha_24h


def get_pas(ps, imax):
    """
    计算前期影响雨量Pa
    :param ps: list 各设计频率
    :param imax: float 最大初损值
    :return: en(hps)D vector
    """
    pas = np.zeros(len(ps))
    for i, p in enumerate(ps):
        pa = imax
        if p > 0.02:
            pa = 2 / 3 * imax
        pas[i] = pa
    return pas


def get_rs(key, ps, hps, imax):
    """
    查 P + Pa~R 关系曲线，获取径流深 R
    :param key: int 曲线代码
    :param ps:  list 各设计频率
    :param hps:  list 各设计频率下的24小时历时设计雨量
    :param imax: float 最大初损值
    :return: len(hps)D vector
    """
    hps = np.array(hps)
    pas = get_pas(ps, imax)
    return np.array([get_relationship_value(key, hps[i] + pas[i]) for i in range(len(hps))])


def get_m(area, theta):
    """
    获取汇流参数m 查图 θ~m曲线
    已对汇流参数曲线进行拟合，这里使用拟合后的函数进行计算。
    :param area: int 所在分区
    :param theta: float θ值
    :return: float 汇流参数值
    """
    if area == 1:
        return 0.314287 * theta ** 0.404842
    if area == 2:
        return 0.478361 * theta ** 0.400535
    if area == 3:
        return 0.575721 * theta ** 0.401817
    if area == 4:
        return 0.417826 * theta ** 0.400506
    if area == 5:
        return 0.511508 * theta ** 0.404065
    if area == 6:
        return 0.511508 * theta ** 0.404065
    return 0.0


def get_mu(area):
    """
    获取平均入渗率，由于关系很简单，不再录入数据库，这里直接按规则判断。
    :param area: int 所在分区
    :return: float 平均入渗率
    """
    if area == 1:
        return 2.0
    if area == 2:
        return 3.0
    if area == 3:
        return 4.0
    if area == 4:
        return 3.0
    if area == 5:
        return 5.0
    if area == 6:
        return 5.0
    return 0.0


if __name__ == '__main__':
    import time
    t1 = time.time()
    # v = get_contour_value(8421, (116, 35))
    # print(v)
    print(get_area(114, 33))
    print(time.time()-t1)

    print(get_relationship_value(8424012, 200))
