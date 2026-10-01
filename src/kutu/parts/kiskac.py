"""Kıskaç ve kıskaç düğümü: aynı düzlemdeki iki paneli ek yerinden birleştiren dikey profil.

Kıskaç (H boyunda) cep ve vida kuleleri taşır; düğüm (2T boyunda, iki kat arası)
yalnızca vida geçiş delikleri taşır.
"""
from functools import cache

from build123d import Align, Box, Cylinder, Part, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva
from kutu.lib.kule import kule

_KULE_Y = (p.CEP_IC + p.K - p.WALL) / 2


def _profil(z0: float, h: float) -> Part:
    govde = Pos(-p.K, p.GAP, z0) * Box(2 * p.K, p.K - p.GAP, h, align=MIN3)
    govde -= yuva(-p.K, -p.K + p.DIL + p.FIT, z0, z0 + h)
    govde -= yuva(p.K - p.DIL - p.FIT, p.K, z0, z0 + h)
    return govde


@cache
def kiskac() -> Part:
    govde = _profil(p.T, p.H)

    c0, c1 = p.CEP_IC, p.K - p.WALL
    cx = p.KISKAC_CEP_YARI
    cep = Box(2 * cx, c1 - c0, p.CEP_BOY, align=MIN3)
    govde -= Pos(-cx, c0, p.T) * cep
    govde -= Pos(-cx, c0, p.T + p.H - p.CEP_BOY) * cep

    for x in (-p.KISKAC_KULE_X, p.KISKAC_KULE_X):
        govde += Pos(x, _KULE_Y, p.T) * kule(p.CEP_BOY)
        govde += Pos(x, _KULE_Y, p.T + p.H) * Rot(180, 0, 0) * kule(p.CEP_BOY)
    return govde


@cache
def kiskac_dugumu() -> Part:
    """İki kat arasındaki kıskaç bağlantısı (T+H … T+H+2T)."""
    z0 = p.T + p.H
    govde = _profil(z0, 2 * p.T)
    for x in (-p.KISKAC_KULE_X, p.KISKAC_KULE_X):
        govde -= Pos(x, _KULE_Y, z0) * Cylinder(
            p.GECIS_DELIK / 2, 2 * p.T, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
    return govde
