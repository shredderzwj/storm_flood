# -*- coding:utf-8 -*-

from .tables import AreaTable, RelationshipTable, ContourTable
from .conf import proj

area_info = {
    1: "山丘I区",
    2: "山丘II区",
    3: "山丘III区",
    4: "山丘IV区",
    5: "山丘V区",
    6: "山丘VI区",
    7: "平原区",
}

contour_info = {
    # type： [图名， 用于计算的变量名]
    8402: ['年最大10min点雨量均值', 'yl_1'],
    8403: ['年最大10min点雨量Cv', 'cv_1'],
    8405: ['年最大1h点雨量均值', 'yl_2'],
    8406: ['年最大1h点雨量Cv', 'cv_2'],
    8408: ['年最大6h点雨量均值', 'yl_3'],
    8409: ['年最大6h点雨量Cv', 'cv_3'],
    8411: ['年最大24h点雨量均值', 'yl_4'],
    8412: ['年最大24h点雨量Cv', 'cv_4'],
    8421: ['暴雨递减指数n1', 'n1'],
    8422: ['暴雨递减指数n2', 'n2'],
    8423: ['暴雨递减指数n3', 'n3'],
}

relationship_info = {
    8424101: "84图集山丘I区10分钟历时暴雨时面深关系（t-F-α）",
    8424011: "84图集山丘I区1小时历时暴雨时面深关系（t-F-α）",
    8424061: "84图集山丘I区6小时历时暴雨时面深关系（t-F-α）",
    8424241: "84图集山丘I区24小时历时暴雨时面深关系（t-F-α）",
    8424031: "84图集山丘I区3天历时暴雨时面深关系（t-F-α）",
    8424102: "84图集山丘II、III、IV区10分钟历时暴雨时面深关系（t-F-α）",
    8424012: "84图集山丘II、III、IV区1小时历时暴雨时面深关系（t-F-α）",
    8424062: "84图集山丘II、III、IV区6小时历时暴雨时面深关系（t-F-α）",
    8424242: "84图集山丘II、III、IV区24小时历时暴雨时面深关系（t-F-α）",
    8424032: "84图集山丘II、III、IV区3天历时暴雨时面深关系（t-F-α）",
    8424103: "84图集山丘V、VI区10分钟历时暴雨时面深关系（t-F-α）",
    8424013: "84图集山丘V、VI区1小时历时暴雨时面深关系（t-F-α）",
    8424063: "84图集山丘V、VI区6小时历时暴雨时面深关系（t-F-α）",
    8424243: "84图集山丘V、VI区24小时历时暴雨时面深关系（t-F-α）",
    8424033: "84图集山丘V、VI区3天历时暴雨时面深关系（t-F-α）",
    842500: "84图集山丘区各频率下最大初损值系数（Imax）",
    842501: "84图集山丘I区降雨径流关系（P+Pa--R I曲线）",
    842502: "84图集山丘II区降雨径流关系（P+Pa--R II曲线）",
    842503: "84图集山丘III区降雨径流关系（P+Pa--R III曲线）",
    842504: "84图集山丘IV区降雨径流关系（P+Pa--R IV曲线）",
    842505: "84图集山丘V区降雨径流关系（P+Pa--R V曲线）",
    842506: "84图集山丘VI-1区降雨径流关系（P+Pa--R VI-1曲线）",
    842507: "84图集山丘VI-2区降雨径流关系（P+Pa--R VI-2曲线）",
    842508: "84图集山丘VI-3区降雨径流关系（P+Pa--R VI-3曲线）",
    842601: "84图集推理公式汇流参数θ~m地区综合关系（山丘I区）",
    842602: "84图集推理公式汇流参数θ~m地区综合关系（山丘II区）",
    842603: "84图集推理公式汇流参数θ~m地区综合关系（山丘III区）",
    842604: "84图集推理公式汇流参数θ~m地区综合关系（山丘IV区）",
    842605: "84图集推理公式汇流参数θ~m地区综合关系（山丘V区）",
    734700: "73图集平原区各频率下最大初损值系数（Imax）",
    734701: "73图集降雨径流关系（P+Pa--R I曲线）",
    734702: "73图集降雨径流关系（P+Pa--R II曲线）",
    734703: "73图集降雨径流关系（P+Pa--R III曲线）",
    734704: "73图集降雨径流关系（P+Pa--R IV曲线）",
    734705: "73图集降雨径流关系（P+Pa--R V曲线）",
    734706: "73图集降雨径流关系（P+Pa--R VI曲线）",
    734707: "73图集降雨径流关系（P+Pa--R VII曲线）",
    734708: "73图集降雨径流关系（P+Pa--R VIII曲线）",
}

area = {}
for k in area_info.keys():
    infos = []
    for item in AreaTable.get_data('type', k):
        info = (item['lon'], item['lat'])
        infos.append(info)
    area[k] = infos

contour = {}
for k in contour_info.keys():
    infos = []
    for item in ContourTable.get_data('type', k):
        info = (*proj(item['lon'], item['lat']), item['value'])
        infos.append(info)
    contour[k] = infos

relationship = {}
for k in relationship_info.keys():
    infos = []
    for item in RelationshipTable.get_data('type', k):
        info = (item['x'], item['y'])
        infos.append(info)
    relationship[k] = infos

if __name__ == '__main__':
    print(relationship)
