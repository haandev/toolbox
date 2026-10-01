"""Gömme kulp: 1×, 2×, 3× node boyunda; tek parça tavanın içindeki oyukta katlı yatar.

Yerel çerçeve: x kulp bölgesi boyunca (0 … n·P_XY), y = 0 kulbun orta çizgisi (kutunun
ortası), z = 0 tavanın kilit yüzü. Katlıyken kulp z = −1−KULP_H … −1 arasında, kilit
yüzünün altında; mafsal ekseni x boyunca, y = −KULP_KOL, z = MAFSAL_Z.
"""
from functools import cache

from build123d import Box, Cylinder, Part, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3

EKSEN_Y = -p.KULP_KOL
MAFSAL_Z = -1 - p.KULP_H / 2
KULP_Z0, KULP_Z1 = -1 - p.KULP_H, -1.0


def kulp_x0() -> float:
    """Kulp kolunun dış yüzü (kulp bölgesi başından)."""
    return p.K + p.WALL + p.MAFSAL_L + p.FIT


@cache
def kulp(n: int) -> Part:
    x0 = kulp_x0()
    x1 = n * p.P_XY - x0
    h = KULP_Z1 - KULP_Z0
    govde = Pos(x0, -p.KULP_W / 2, KULP_Z0) * Box(x1 - x0, p.KULP_W, h, align=MIN3)   # tutma yeri
    kol_y0 = EKSEN_Y - p.MAFSAL_W / 2
    for kx in (x0, x1 - p.KOL_T):
        govde += Pos(kx, kol_y0, KULP_Z0) * Box(p.KOL_T, p.KULP_W / 2 - kol_y0, h, align=MIN3)   # kollar
    pim_boy = p.MAFSAL_L - 1
    pim = Rot(0, 90, 0) * Cylinder(p.PIM_D / 2, pim_boy)
    govde += Pos(x0 - pim_boy / 2, EKSEN_Y, MAFSAL_Z) * pim
    govde += Pos(x1 + pim_boy / 2, EKSEN_Y, MAFSAL_Z) * pim
    return govde


def acik(parca: Part) -> Part:
    """Katlı kulbu mafsal ekseni etrafında 90° kaldırır."""
    return Pos(0, EKSEN_Y, MAFSAL_Z) * Rot(90, 0, 0) * Pos(0, -EKSEN_Y, -MAFSAL_Z) * parca
