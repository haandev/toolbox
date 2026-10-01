"""Çekmece ve kat arası raf.

Çekmece (node çerçevesi: x 0 … P_XY, y kutu ön yüzünden içe, z kutu çerçevesi): ön plaka
panelin yerini kapatır ve panel dış yüzüyle aynı hizadadır; arkasında tepsi. Ön plakanın
üst ortasında parmak girintisi. Tepsi tabanın / rafın üstünde FIT boşlukla kayar.
Raf (kutu çerçevesi): kat arasında yatay kıskaçların iç çıkıntılarına oturur; köşe ve
kıskaç izlerinde çentikli. Kutu boyuna göre tek parça.
"""
from functools import cache

from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y


def _k(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


@cache
def cekmece(plaka_z0: float, plaka_z1: float, tepsi_z0: float, tepsi_z1: float) -> Part:
    x0, x1 = p.K + p.CEKMECE_B, p.P_XY - p.K - p.CEKMECE_B
    y0, y1 = panel_y()
    arka = p.P_XY - (p.GAP + p.LIP + p.WALL + p.RIB_D) - p.FIT    # arka panel kaburgalarının önü
    plaka = _k(x0, x1, y0, y1, plaka_z0, plaka_z1)
    c = p.P_XY / 2
    plaka -= _k(c - p.CEKMECE_TUTAMAK_W / 2, c + p.CEKMECE_TUTAMAK_W / 2, y0 - 1, y1 + 1,
                plaka_z1 - p.CEKMECE_TUTAMAK_H, plaka_z1 + 1)
    w = p.WALL
    tepsi = _k(x0, x1, y1, arka, tepsi_z0, tepsi_z1)
    tepsi -= _k(x0 + w, x1 - w, y1, arka - w, tepsi_z0 + w, tepsi_z1 + 1)
    return plaka + tepsi


@cache
def raf(nx: int, ny: int, kat: int) -> Part:
    """kat ile kat+1 arasındaki raf (kutu çerçevesinde)."""
    W, D = nx * p.P_XY, ny * p.P_XY
    z0 = kat * p.P_Z + p.T + p.H + 2 * p.T
    e = p.RAF_KENAR
    r = _k(e, W - e, e, D - e, z0, z0 + p.WALL)
    k = p.K + p.FIT
    for x in (0, W):                       # köşe izleri
        for y in (0, D):
            r -= _k(x - k, x + k, y - k, y + k, z0 - 1, z0 + p.WALL + 1)
    for i in range(1, nx):                 # ön/arka kıskaç izleri
        for y in (0, D):
            r -= _k(i * p.P_XY - k, i * p.P_XY + k, y - k, y + k, z0 - 1, z0 + p.WALL + 1)
    for j in range(1, ny):                 # yan kıskaç izleri
        for x in (0, W):
            r -= _k(x - k, x + k, j * p.P_XY - k, j * p.P_XY + k, z0 - 1, z0 + p.WALL + 1)
    return r
