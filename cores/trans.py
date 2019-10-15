# -*- coding:utf-8 -*-

import numpy as np
from itertools import combinations
import pandas as pd
import sys
import os

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

from cores.tables import DB, AreaTable, RelationshipTable, ContourTable


class Trans(object):
    def __init__(self, proj, p_xys, p_lls):
        self.proj = proj
        ks = []
        for (i, j) in combinations(range(len(p_xys)), 2):
            p1 = np.array(proj(*p_lls[i]))
            p2 = np.array(proj(*p_lls[j]))
            distance_meter = self.distance(p1, p2)
            distance_pic = self.distance(p_xys[i], p_xys[j])
            k = distance_meter / distance_pic
            ks.append(k)
        self.k = sum(ks) / len(ks)
        dps = np.array([0, 0])
        for i, xy in enumerate(p_xys):
            dps = dps[:] + np.array(proj(*p_lls[i])) - np.array(xy) * self.k
        self.dp = dps / len(p_xys)

    @staticmethod
    def distance(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def __call__(self, x, y):
        p = np.array([x, y]) * self.k + self.dp
        return self.proj(*p, inverse=True)


def trans_area(proj):
    df = pd.read_csv(os.path.join('data', 'area_trans.csv'))
    xys = list(zip(df.x, df.y))
    lls = list(zip(df.lon, df.lat))
    t = Trans(proj, xys, lls)
    ps = []
    for i in range(1, 8):
        with open(os.path.join("data", 'area%d.dat' % i), 'r') as fp:
            ps += [list(map(lambda y: float(y), x.strip().split(','))) + [i] for x in fp.read().split('\n') if x]
    items = []
    for p in ps:
        lon, lat, area = list(t(*p[:-1])) + [p[-1]]
        items.append(
            {
                'lon': lon,
                'lat': lat,
                'type': area,
            }
        )
    AreaTable.insert_many(items)
    print('insert area')


def trans_contour(proj, trans_file, file, type_value):
    df = pd.read_csv(os.path.join('data', trans_file))
    xys = list(zip(df.x, df.y))
    lls = list(zip(df.lon, df.lat))
    t = Trans(proj, xys, lls)
    with open(os.path.join('data', file)) as fp:
        data = [list(map(lambda y: float(y), x.strip().split(','))) for x in fp.read().split('\n') if x]
    items = []
    for p in data:
        lon, lat, value = list(t(*p[:-1])) + [p[-1]]
        items.append(
            {
                'lon': lon,
                'lat': lat,
                'value': value,
                'type': type_value,
            }
        )
    ContourTable.insert_many(items)
    print('insert contour -> %d' % type_value)


def trans_relationship(file, type_value):
    with open(os.path.join('data', file)) as fp:
        infos = [list(map(lambda y: float(y), x.strip().split(','))) for x in fp.read().split('\n') if x]
    items = []
    for info in infos:
        x, y = info
        items.append(
            {
                'x': x,
                'y': y,
                'type': type_value,
            }
        )
    RelationshipTable.insert_many(items)
    print('insert relationship -> %d' % type_value)


if __name__ == '__main__':
    from cores.conf import proj

    contour_info = {
        8402: "TU2_10mDYLJZ.dat",
        8403: "TU3_10mCV.dat",
        8405: "TU5_1hDYLJZ.dat",
        8406: "TU6_1hCV.dat",
        8408: "TU8_6hDYLJZ.dat",
        8409: "TU9_6hCV.dat",
        8411: "TU11_24hDYLJZ.dat",
        8412: "TU12_24hCV.dat",
        8421: "TU21_n1.dat",
        8422: "TU22_n2.dat",
        8423: "TU23_n3.dat",
    }

    relationship_info = {
        8424101: "t-F-arfa_area1_10min.dat",
        8424011: "t-F-arfa_area1_1h.dat",
        8424061: "t-F-arfa_area1_6h.dat",
        8424241: "t-F-arfa_area1_24h.dat",
        8424031: "t-F-arfa_area1_3d.dat",
        8424102: "t-F-arfa_area234_10min.dat",
        8424012: "t-F-arfa_area234_1h.dat",
        8424062: "t-F-arfa_area234_6h.dat",
        8424242: "t-F-arfa_area234_24h.dat",
        8424032: "t-F-arfa_area234_3d.dat",
        8424103: "t-F-arfa_area56_10min.dat",
        8424013: "t-F-arfa_area56_1h.dat",
        8424063: "t-F-arfa_area56_6h.dat",
        8424243: "t-F-arfa_area56_24h.dat",
        8424033: "t-F-arfa_area56_3d.dat",
        842500: "Imax--Pa_SQ.dat",
        842501: "P+Pa--R_area1.dat",
        842502: "P+Pa--R_area2.dat",
        842503: "P+Pa--R_area3.dat",
        842504: "P+Pa--R_area4.dat",
        842505: "P+Pa--R_area5.dat",
        842506: "P+Pa--R_area61.dat",
        842507: "P+Pa--R_area62.dat",
        842508: "P+Pa--R_area63.dat",
        842601: "Seita-m_area1.dat",
        842602: "Seita-m_area2.dat",
        842603: "Seita-m_area3.dat",
        842604: "Seita-m_area4.dat",
        842605: "Seita-m_area5.dat",
        734700: "Imax--Pa_PY.dat",
        734701: "P+Pa--R_areaPY1.dat",
        734702: "P+Pa--R_areaPY2.dat",
        734703: "P+Pa--R_areaPY3.dat",
        734704: "P+Pa--R_areaPY4.dat",
        734705: "P+Pa--R_areaPY5.dat",
        734706: "P+Pa--R_areaPY6.dat",
        734707: "P+Pa--R_areaPY7.dat",
        734708: "P+Pa--R_areaPY8.dat",
    }
    if os.path.exists(DB.db_file_path):
        print('数据已经转换迁移，若要重新迁移，请先删除原有数据库文件！')
    else:
        db = DB()
        trans_area(proj)

        for k, v in contour_info.items():
            file = v
            trans_file = v.replace('.dat', '_trans.csv')
            trans_contour(proj, trans_file, file, k)

        for k, v in relationship_info.items():
            trans_relationship(v, k)
