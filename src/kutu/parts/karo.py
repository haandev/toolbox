"""Karo: 1 node'luk taban/tavan plakası. Tavan, aynı parçanın ters çevrilmiş hâlidir."""
from functools import cache

from build123d import Align, Box, Cylinder, Part, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva
from kutu.lib.kilit_yeri import karo_bolgesi

_C = p.P_XY / 2


def _dondur(x: float, y: float, aci: int) -> tuple[float, float]:
    dx, dy = x - _C, y - _C
    for _ in range(aci // 90):
        dx, dy = -dy, dx
    return (_C + dx, _C + dy)


def delik_noktalari() -> list[tuple[float, float]]:
    """Her köşede: köşe kulesi + iki komşu kıskaç kulesi; 4 köşe → 12 delik."""
    m = p.KOSE_KULE
    km = (p.CEP_IC + p.K - p.WALL) / 2
    gb = [(m, m), (p.KISKAC_KULE_X, km), (km, p.KISKAC_KULE_X)]
    return [_dondur(x, y, a) for a in (0, 90, 180, 270) for x, y in gb]


@cache
def karo() -> Part:
    g = p.GAP
    L = p.P_XY - 2 * g
    plaka = Pos(g, g, g) * Box(L, L, p.T - g, align=MIN3)

    # iç bölge alttan boşaltılır, üstte WALL kalınlığında güverte kalır; kenarda K genişliğinde çerçeve
    ic_L = p.P_XY - 2 * p.K
    ic_h = p.T - g - p.WALL
    plaka -= Pos(p.K, p.K, g) * Box(ic_L, ic_L, ic_h, align=MIN3)

    # güverte altı kaburga ızgarası
    kaburga = None
    x = p.K + p.KARO_RIB_ARALIK
    while x < p.P_XY - p.K - 1e-6:
        dx = Pos(x - p.RIB / 2, p.K, g) * Box(p.RIB, ic_L, ic_h, align=MIN3)
        dy = Pos(p.K, x - p.RIB / 2, g) * Box(ic_L, p.RIB, ic_h, align=MIN3)
        kaburga = dx + dy if kaburga is None else kaburga + dx + dy
        x += p.KARO_RIB_ARALIK
    kaburga -= karo_bolgesi()
    plaka += kaburga

    # dört kenarda panel oluğu (üst yüzden DIL+FIT derin)
    oluk = yuva(g, p.P_XY - g, p.T - p.DIL - p.FIT, p.T)
    for aci in (0, 90, 180, 270):
        plaka -= Pos(_C, _C, 0) * Rot(0, 0, aci) * Pos(-_C, -_C, 0) * oluk

    # vida geçiş delikleri
    for x, y in delik_noktalari():
        plaka -= Pos(x, y, 0) * Cylinder(
            p.GECIS_DELIK / 2, p.T, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
    return plaka
