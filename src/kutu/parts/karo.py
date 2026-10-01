"""Karo: 1 node'luk taban ve tavan plakaları.

Ortak gövde: oluk yüzü +z, kilit yüzü z = GAP (alttan oyuk, kaburgalı).
Dikey istif: tavanın (parts/tavan.py) T rayları taban karosunun iki yönlü T kanallarına girer
(öne kayan istif, dikey kilit, yan hizalama).
"""
from functools import cache

from build123d import Align, Box, Cylinder, Part, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import anahtar_cebi, yuva
from kutu.lib.kilit_yeri import karo_bolgesi
from kutu.parts.cekmece import durdurucu
from kutu.parts.t_kanal import kanal_duvarlari, kanal_kesimi

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


def _govde(kaburga_kes: Part | None) -> Part:
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
    if kaburga_kes is not None:
        kaburga -= kaburga_kes
    plaka += kaburga

    # dört kenarda panel oluğu (üst yüzden DIL_V+FIT derin)
    oluk = yuva(g, p.P_XY - g, p.T - p.DIL_V - p.FIT, p.T)
    for aci in (0, 90, 180, 270):
        plaka -= Pos(_C, _C, 0) * Rot(0, 0, aci) * Pos(-_C, -_C, 0) * oluk

    # vida geçiş delikleri
    for x, y in delik_noktalari():
        plaka -= Pos(x, y, 0) * Cylinder(
            p.GECIS_DELIK / 2, p.T, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
    return plaka


_IC = p.P_XY - 2 * p.K


@cache
def karo_taban() -> Part:
    taban = _govde(None)
    cep = Pos(_C, 0, 0) * anahtar_cebi(p.T - p.DIL_V - p.FIT, p.T)   # güney duvar
    for aci in (0, 90, 180, 270):
        taban -= Pos(_C, _C, 0) * Rot(0, 0, aci) * Pos(-_C, -_C, 0) * cep
    for aci in (0, 90):                                # T kanallar iki yönde (döndürülmüş istif)
        yer = Pos(_C, _C, 0) * Rot(0, 0, aci) * Pos(-_C, -_C, 0)
        taban += yer * kanal_duvarlari()
    for aci in (0, 90):
        taban -= Pos(_C, _C, 0) * Rot(0, 0, aci) * Pos(-_C, -_C, 0) * kanal_kesimi()
    for aci in (0, 90, 180, 270):                      # çekmece durdurucusu her kenarda (çerçeve üstünde)
        taban += Pos(_C, _C, 0) * Rot(0, 0, aci) * Pos(-_C, -_C, 0) * durdurucu(_C, p.T)
    return taban
