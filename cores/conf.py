# -*- coding:utf-8 -*-

from pyproj import Proj


bj54_str = "+a=6378245 +b=6356863 +rf=298.3"
xa80_str = '+a=6378140 +b=6356755 +rf=298.25722101'
proj = Proj('+proj=lcc  +lat_0=34 +lat_1=34 +lat_2=34 +lon_0=114 %s' % bj54_str)
