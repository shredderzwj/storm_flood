# -*- coding:utf-8 -*-

import os


def path_tree(file_name, tp='file'):
    """
    获取文件的路径树各节点
    tp为'path'时， 输入的路径是文件夹路径，默认为'file'为文件路径
    """
    file_name = os.path.abspath(file_name)
    if tp == 'path':
        pts = [file_name]
    else:
        pts = [os.path.dirname(file_name)]
    while True:
        pt = os.path.dirname(pts[-1])
        if pts[-1] == pt:
            pts.reverse()
            return pts
        else:
            pts.append(pt)


def create_path_tree(file_name, tp='file'):
    for path_ in path_tree(file_name, tp):
        if not os.path.exists(path_):
            os.mkdir(path_)
