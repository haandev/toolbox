"""Kıskaç: aynı düzlemdeki iki paneli ek yerinden birleştiren dikey profil."""
from functools import cache

from build123d import Box, Part, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva
from kutu.lib.kule import kule


@cache
def kiskac() -> Part:
    govde = Pos(-p.K, p.GAP, p.T) * Box(2 * p.K, p.K - p.GAP, p.H, align=MIN3)
    govde -= yuva(-p.K, -p.K + p.DIL + p.FIT, p.T, p.T + p.H)
    govde -= yuva(p.K - p.DIL - p.FIT, p.K, p.T, p.T + p.H)

    c0, c1 = p.CEP_IC, p.K - p.WALL
    cx = p.KISKAC_CEP_YARI
    cep = Box(2 * cx, c1 - c0, p.CEP_BOY, align=MIN3)
    govde -= Pos(-cx, c0, p.T) * cep
    govde -= Pos(-cx, c0, p.T + p.H - p.CEP_BOY) * cep

    m = (c0 + c1) / 2
    for x in (-p.KISKAC_KULE_X, p.KISKAC_KULE_X):
        govde += Pos(x, m, p.T) * kule(p.CEP_BOY)
        govde += Pos(x, m, p.T + p.H) * Rot(180, 0, 0) * kule(p.CEP_BOY)
    return govde
