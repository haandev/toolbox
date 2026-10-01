"""Tavan: kutu boyuna göre tek parça (nx × ny node).

Yerel çerçeve: x, y kutu ızgarası (0 … nx·P_XY), z = 0 kutunun nominal üstü.
Gövde: kenar çerçevesi (altta panel oluğu), altta güverte, üstte kaburgalı cep, kilit yüzü
z = −GAP. Her node sütununda ön–arka boyunca iki kılavuz ray kilit yüzünden KILAVUZ_H taşar;
üstteki kutunun taban cebine x'te FIT ile oturur, y'de serbest (kutu öne kayarak çıkar). Ortada gömme kulp oyuğu (kilit yüzünün altında,
kutunun içine sarkan tekne) ve mafsal blokları.
"""
from functools import cache

from build123d import Align, Box, Cylinder, Part, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import anahtar_cebi, yuva
from kutu.parts.karo import delik_noktalari
from kutu.parts.kulp import EKSEN_Y, KULP_Z0, MAFSAL_Z, kulp_x0
from kutu.parts.mandal import tavan_cebi


def kulp_boyu(nx: int) -> int:
    return min(nx, 3)


def kulp_yeri(nx: int, ny: int) -> tuple[float, float]:
    """Kulp bölgesinin başlangıç x'i ve orta çizgisinin y'si (kutu çerçevesi)."""
    n = kulp_boyu(nx)
    return (nx * p.P_XY - n * p.P_XY) / 2, ny * p.P_XY / 2


def _kutu(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


def _duvar_yerlesimleri(W: float, D: float, nx: int, ny: int):
    """(yerleşim, baş aşağı mı) — batı ve kuzey panelleri baş aşağı takılır."""
    c = p.P_XY / 2
    for i in range(nx):
        yield Pos(c + i * p.P_XY, 0, 0), False
        yield Pos(c + i * p.P_XY, D, 0) * Rot(0, 0, 180), True
    for j in range(ny):
        yield Pos(0, c + j * p.P_XY, 0) * Rot(0, 0, -90), True
        yield Pos(W, c + j * p.P_XY, 0) * Rot(0, 0, 90), False


def _govde(nx: int, ny: int) -> Part:
    g, W, D = p.GAP, nx * p.P_XY, ny * p.P_XY
    alt, kilit = -p.T, -g
    t = _kutu(g, W - g, g, D - g, alt, kilit)
    t -= _kutu(p.K, W - p.K, p.K, D - p.K, alt + p.WALL, kilit)            # üstten kaburgalı cep

    x = p.K + p.KARO_RIB_ARALIK
    while x < W - p.K - 1e-6:
        t += _kutu(x - p.RIB / 2, x + p.RIB / 2, p.K, D - p.K, alt + p.WALL, kilit)
        x += p.KARO_RIB_ARALIK
    y = p.K + p.KARO_RIB_ARALIK
    while y < D - p.K - 1e-6:
        t += _kutu(p.K, W - p.K, y - p.RIB / 2, y + p.RIB / 2, alt + p.WALL, kilit)
        y += p.KARO_RIB_ARALIK

    # dış kenarlarda panel oluğu (alttan) ve yan kilit çentiği
    for yer, bas_asagi in _duvar_yerlesimleri(W, D, nx, ny):
        t -= yer * yuva(-p.P_XY / 2, p.P_XY / 2, alt, alt + p.DIL + p.FIT)
        if bas_asagi:                    # baş aşağı panelin anahtarı üstte, x = −ANAHTAR_X
            t -= yer * anahtar_cebi(alt, alt + p.DIL + p.FIT, x=-p.ANAHTAR_X)

    # köşe ve kıskaç vida delikleri (yalnız dış kenara yakın olanlar)
    for i in range(nx):
        for j in range(ny):
            for hx, hy in delik_noktalari():
                x, y = hx + i * p.P_XY, hy + j * p.P_XY
                if min(x, y, W - x, D - y) < p.K:
                    t -= Pos(x, y, alt) * Cylinder(p.GECIS_DELIK / 2, p.T,
                                                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    return t


def _kilavuzlar(nx: int, ny: int) -> Part:
    a, w = p.KILAVUZ_A, p.WALL
    D = ny * p.P_XY
    z0, z1 = -p.GAP - 1.0, p.KILAVUZ_H - p.GAP   # çerçeve ve kaburgaların üstüne oturur, panel oluğuna inmez
    pah = p.KILAVUZ_PAH
    tum = None
    for i in range(nx):
        for x in (i * p.P_XY + a, (i + 1) * p.P_XY - a - w):
            ray = _kutu(x, x + w, p.GAP, D - p.GAP, z0, z1)
            # ön ve arka uçta üst kenar pahı (kayarak giriş)
            for y0, y1 in ((p.GAP, p.GAP + pah), (D - p.GAP - pah, D - p.GAP)):
                ray -= _kutu(x - 1, x + w + 1, y0 - 0.01, y1 + 0.01, z1 - pah, z1 + 1)
            tum = ray if tum is None else tum + ray
    return tum


def _kulp_bolgeleri(nx: int, ny: int):
    """(oyuk, süpürme zarfı, mafsal blokları) — kutu çerçevesinde."""
    n = kulp_boyu(nx)
    xs, yc = kulp_yeri(nx, ny)
    x0 = xs + kulp_x0()
    x1 = xs + n * p.P_XY - kulp_x0()
    bx0, bx1 = x0 - p.FIT - p.MAFSAL_L, x1 + p.FIT + p.MAFSAL_L
    kilit = -p.GAP
    taban = kilit + KULP_Z0 - 1
    ey = yc + EKSEN_Y
    oyuk = (_kutu(x0 - 1, x1 + 1, yc - p.KULP_W / 2 - 1, yc + p.KULP_W / 2 + 1, taban, kilit + 1)
            + _kutu(bx0, x0 + p.KOL_T + 1, ey - p.MAFSAL_W / 2 - 1, yc, taban, kilit + 1)
            + _kutu(x1 - p.KOL_T - 1, bx1, ey - p.MAFSAL_W / 2 - 1, yc, taban, kilit + 1))
    zarf = _kutu(x0 - 1, x1 + 1, ey - p.KULP_W / 2 - 2, yc + p.KULP_W / 2 + 2, kilit, p.KILAVUZ_H + 1)
    mz = kilit + MAFSAL_Z
    bloklar = None
    for bx in (bx0, x1 + p.FIT):
        blok = _kutu(bx, bx + p.MAFSAL_L, ey - p.MAFSAL_W / 2, ey + p.MAFSAL_W / 2, taban, kilit - 1)
        blok -= Pos(bx + p.MAFSAL_L / 2, ey, mz) * Rot(0, 90, 0) * Cylinder(p.PIM_D / 2 + p.FIT, p.MAFSAL_L + 1)
        bloklar = blok if bloklar is None else bloklar + blok
    return oyuk, zarf, bloklar


@cache
def tavan(nx: int, ny: int) -> Part:
    oyuk, zarf, bloklar = _kulp_bolgeleri(nx, ny)
    # tekne: oyuğun WALL kalınlığında kabuğu, kutunun içine sarkar
    bb = oyuk.bounding_box()
    tekne = None
    for parca in oyuk.solids():
        b = parca.bounding_box()
        kabuk = _kutu(b.min.X - p.WALL, b.max.X + p.WALL, b.min.Y - p.WALL, b.max.Y + p.WALL,
                      b.min.Z - p.WALL, -p.GAP)
        tekne = kabuk if tekne is None else tekne + kabuk
    t = _govde(nx, ny) + tekne - oyuk + bloklar
    t += _kilavuzlar(nx, ny) - zarf      # oyuktan sonra: ray kenarı oyuk ağzından kesilmez
    for yer in mandal_yerleri(nx, ny):
        t -= yer * tavan_cebi()
    return t


def mandal_yerleri(nx: int, ny: int):
    """Her node'un ön (güney) ve arka (kuzey) kenarındaki mandal dönüşümleri."""
    c = p.P_XY / 2
    W, D = nx * p.P_XY, ny * p.P_XY
    for i in range(nx):
        yield Pos(i * p.P_XY, 0, 0)
        yield Pos(i * p.P_XY, D - p.P_XY, 0) * Pos(c, c, 0) * Rot(0, 0, 180) * Pos(-c, -c, 0)
