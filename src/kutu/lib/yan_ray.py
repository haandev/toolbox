"""Yan ray geometrisi (panel çerçevesi: u = x boyunca, y kutu yüzünden içe, z kat tabanından).

Normal panelde dil v₁'de, oluk v₂'de; v₁ ve v₂ panel orta yüksekliğine simetrik olduğu
için baş aşağı takılan panelde yer değiştirir. Komşu kutunun yüzü y = −GAP'tedir.
"""
from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3

OLUK_DERIN = p.RAY_T - 2 * p.GAP + p.FIT     # şerit yüzünden (y = GAP) itibaren


def _k(u0, u1, y0, y1, z0, z1) -> Part:
    return Pos(u0, y0, z0) * Box(u1 - u0, y1 - y0, z1 - z0, align=MIN3)


def serit(u0: float, u1: float) -> Part:
    """Panelin gömük yüzünü ray yüksekliklerinde kutu yüzüne kadar dolduran şeritler."""
    h = p.RAY_H / 2 + p.FIT + p.WALL
    y0, y1 = p.GAP, p.GAP + p.LIP
    return _k(u0, u1, y0, y1, p.RAY_V1 - h, p.RAY_V1 + h) + _k(u0, u1, y0, y1, p.RAY_V2 - h, p.RAY_V2 + h)


def dil(u0: float, u1: float) -> Part:
    h = p.RAY_H / 2
    return _k(u0, u1, p.GAP - p.RAY_T, p.GAP + 0.01, p.RAY_V1 - h, p.RAY_V1 + h)


def oluk(u0: float, u1: float, v: float) -> Part:
    h = p.RAY_H / 2 + p.FIT
    return _k(u0, u1, p.GAP - 0.01, p.GAP + OLUK_DERIN, v - h, v + h)


def dis_oluklar(u0: float, u1: float) -> Part:
    """Köşe/kıskaç dış yüzünde, komşu dilinin geçeceği iki yükseklikteki oluk."""
    return oluk(u0, u1, p.RAY_V1) + oluk(u0, u1, p.RAY_V2)


def dis_oluklar_y(v0: float, v1: float) -> Part:
    """dis_oluklar'ın x↔y aynası: dış yüzü x = GAP olan profil için (köşenin batı yüzü)."""
    h = p.RAY_H / 2 + p.FIT
    tum = None
    for v in (p.RAY_V1, p.RAY_V2):
        o = Pos(p.GAP - 0.01, v0, v - h) * Box(OLUK_DERIN + 0.01, v1 - v0, 2 * h, align=MIN3)
        tum = o if tum is None else tum + o
    return tum
