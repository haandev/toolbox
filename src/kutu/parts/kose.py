"""Köşe ve köşe düğümü: iki duvar kanalı olan dikey profil.

Köşe (H boyunda) alt/üst cep ve vida kulesi taşır; düğüm (2T boyunda, iki kat arası)
yalnızca vida geçiş deliği taşır.
"""
from functools import cache

from build123d import Align, Axis, Box, Cylinder, Part, Pos, Rot, Vector

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva, yuva_y
from kutu.lib.kule import kule
from kutu.lib import yan_ray


def _profil(z0: float, h: float) -> Part:
    g = p.GAP
    govde = Pos(g, g, z0) * Box(p.K - g, p.K - g, h, align=MIN3)
    dis_kenar = govde.edges().filter_by(Axis.Z).sort_by_distance(Vector(g, g, z0))[0]
    govde = govde.fillet(p.KOSE_R, [dis_kenar])

    # güney kanalı (dil +x yönünde girer) ve batı kanalı (dil +y yönünde girer)
    y0, y1 = yuva_y()
    x0 = p.K - p.DIL - p.FIT
    govde -= yuva(x0, p.K, z0, z0 + h)
    govde -= Pos(y0, x0, z0) * Box(y1 - y0, p.K - x0, h, align=MIN3)
    return govde


@cache
def kose() -> Part:
    govde = _profil(p.T, p.H)
    if p.YAN_KILIT:                      # komşu dilinin geçeceği oluklar (güney ve batı dış yüzü)
        govde -= yan_ray.dis_oluklar(0, p.K + 0.01)
        govde -= yan_ray.dis_oluklar_y(0, p.K + 0.01)

    # alt ve üst cepler, ortada WALL kalınlığında ara duvar
    c0, c1 = p.CEP_IC, p.K - p.WALL
    cep = Box(c1 - c0, c1 - c0, p.CEP_BOY, align=MIN3)
    govde -= Pos(c0, c0, p.T) * cep
    govde -= Pos(c0, c0, p.T + p.H - p.CEP_BOY) * cep

    m = p.KOSE_KULE
    govde += Pos(m, m, p.T) * kule(p.CEP_BOY)
    govde += Pos(m, m, p.T + p.H) * Rot(180, 0, 0) * kule(p.CEP_BOY)
    return govde


@cache
def kose_dugumu() -> Part:
    """İki kat arasındaki köşe bağlantısı (T+H … T+H+2T)."""
    z0 = p.T + p.H
    govde = _profil(z0, 2 * p.T)
    m = p.KOSE_KULE
    return govde - Pos(m, m, z0) * Cylinder(
        p.GECIS_DELIK / 2, 2 * p.T, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
