# -*- coding:utf-8 -*-

import numpy as np

from . import calc_common as f
from . import chart


class Calculator(object):
    def __init__(self, **kwargs):
        self.k = kwargs['k']
        self.kwargs = kwargs
        self.area = kwargs['area']
        self.f = kwargs['f']
        self.l = kwargs['l']
        self.j = kwargs['j']
        self.m = kwargs['m']
        self.mu = kwargs['mu']
        self.ps = kwargs['ps']
        self.cvs = kwargs['cvs']
        self.css = kwargs['css']
        self.yls = kwargs['yls']
        self.imax = kwargs['imax']
        self.alphas = kwargs['alphas']
        self.ppa_r_id = kwargs['ppa_r_id']
        # print(kwargs)
        # print(self.ps, self.cvs, self.css)
        if kwargs['is_use_tu_n']:
            self.ns = np.array([np.array([kwargs['n1'], kwargs['n2'], kwargs['n3']]) for _ in self.ps])
        else:
            self.ns = f.calc_ns(*self.design_area_rainfalls.T)
        # self.r24ps = kwargs['r24ps']

    @property
    def r24ps(self):
        key = 842500 + self.ppa_r_id
        h24ps = self.design_area_rainfalls.T[-1]
        return chart.get_rs(key, self.ps, h24ps, self.imax)

    @property
    def kps(self):
        return f.calc_kps(self.ps, self.cvs, self.css)

    @property
    def design_point_rainfalls(self):
        return f.calc_design_point_rainfalls(self.ps, self.cvs, self.css, self.yls)

    @property
    def design_area_rainfalls(self):
        return f.calc_design_area_rainfalls(self.ps, self.cvs, self.css, self.yls, self.alphas)

    @property
    def r_24h_allocate(self):
        # print(tuple((self.r24ps, *self.ns.T[1:], *self.design_area_rainfalls.T[2:])))
        # print(f.calc_r_24h_allocate(self.r24ps, *self.ns.T[1:], *self.design_area_rainfalls.T[2:]))
        return f.calc_r_24h_allocate(self.r24ps, *self.ns.T[1:], *self.design_area_rainfalls.T[2:])

    @property
    def qs(self):
        # ss = [max(rs) for rs in self.per_hour_r]
        ss = self.design_area_rainfalls.T[1]
        qs = f.calc_qs(self.f, self.l, self.j, self.m, self.mu, ss, *self.ns.T[1:])
        return qs

    # @property
    # def psi(self):
    #     ss = self.design_area_rainfalls.T[1]
    #     return f.calc_psi(self.f, self.l, self.j, self.m, self.mu, ss, *self.ns.T[1:])
    #
    # @property
    # def taus(self):
    #     return f.calc_taus(self.l, self.j, self.m, self.qs)

    @property
    def per_hour_r(self):
        return f.calc_per_hour_rps(self.r24ps, self.design_point_rainfalls.T[1],
                                   self.design_point_rainfalls.T[3], *self.ns.T[1:], self.mu)

    @property
    def qs_allocate(self):
        return f.calc_qs_allocate(self.f, self.l, self.j, self.m, self.mu, self.design_area_rainfalls.T[1],
                         *self.ns.T[1:], self.r_24h_allocate)
