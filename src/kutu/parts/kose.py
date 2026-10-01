"""Köşe: iki duvar kanalı, alt/üst cep ve vida kuleleri olan dikey profil."""
from functools import cache

from build123d import Axis, Box, Part, Pos, Rot, Vector

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva, yuva_y
from kutu.lib.kule import kule


def _bati_kanal() -> Part:
    """Güney kanalının x↔y yansıması: batı duvarının dili +y yönünde girer."""
    y0, y1 = yuva_y()
    x0 = p.K - p.DIL - p.FIT
    return Pos(y0, x0, p.T) * Box(y1 - y0, p.K - x0, p.H, align=MIN3)


@cache
def kose() -> Part:
    g = p.GAP
    govde = Pos(g, g, p.T) * Box(p.K - g, p.K - g, p.H, align=MIN3)
    dis_kenar = govde.edges().filter_by(Axis.Z).sort_by_distance(Vector(g, g, p.T))[0]
    govde = govde.fillet(p.KOSE_R, [dis_kenar])

    # güney kanalı (dil +x yönünde girer) ve batı kanalı (dil +y yönünde girer)
    govde -= yuva(p.K - p.DIL - p.FIT, p.K, p.T, p.T + p.H)
    govde -= _bati_kanal()

    # alt ve üst cepler, ortada WALL kalınlığında ara duvar
    c0, c1 = p.CEP_IC, p.K - p.WALL
    cep = Box(c1 - c0, c1 - c0, p.CEP_BOY, align=MIN3)
    govde -= Pos(c0, c0, p.T) * cep
    govde -= Pos(c0, c0, p.T + p.H - p.CEP_BOY) * cep

    m = p.KOSE_KULE
    govde += Pos(m, m, p.T) * kule(p.CEP_BOY)
    govde += Pos(m, m, p.T + p.H) * Rot(180, 0, 0) * kule(p.CEP_BOY)
    return govde
