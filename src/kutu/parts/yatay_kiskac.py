"""Yatay kıskaç: üst üste iki paneli kat arasında birleştiren 2T yüksekliğinde profil.

Yerel çerçeve panel ile aynı (x merkezli, y içe). Altta ve üstte panel oluğu;
iki uçta düğümlerin kanalına giren WALL kalınlığında dil. İç yüzden (+y) oyuk, kaburgalı.
"""
from functools import cache

from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import anahtar_cebi, panel_y, yuva
from kutu.lib.kilit_yeri import yan_oluk


@cache
def yatay_kiskac() -> Part:
    z0, h = p.T + p.H, 2 * p.T
    x_yari = p.U / 2
    govde = Pos(-x_yari, p.GAP, z0) * Box(p.U, p.K - p.GAP, h, align=MIN3)

    # alt oluk (alttaki panelin üst dili) ve üst oluk (üstteki panelin alt dili)
    govde -= yuva(-x_yari, x_yari, z0, z0 + p.DIL + p.FIT)
    govde -= yuva(-x_yari, x_yari, z0 + h - p.DIL - p.FIT, z0 + h)
    govde -= anahtar_cebi(z0 + h - p.DIL - p.FIT, z0 + h)   # üstteki panelin anahtarı

    # içten oyuk: cep +y'ye açık, aralarda kaburga
    cep_x = x_yari - p.WALL
    cep = Pos(-cep_x, p.CEP_IC, z0 + p.WALL) * Box(2 * cep_x, p.K - p.CEP_IC, h - 2 * p.WALL, align=MIN3)
    govde -= cep
    x = -cep_x + p.KARO_RIB_ARALIK
    while x < cep_x - 1e-6:
        govde += Pos(x - p.RIB / 2, p.CEP_IC, z0 + p.WALL) * Box(
            p.RIB, p.K - p.CEP_IC, h - 2 * p.WALL, align=MIN3)
        x += p.KARO_RIB_ARALIK

    # iki uçta düğüm kanalına giren dil; kanalda alt/üst panel dillerinin arasına oturur
    y0, _ = panel_y()
    dil_z0 = z0 + p.DIL + p.FIT
    dil_h = h - 2 * (p.DIL + p.FIT)
    for x0 in (-x_yari - p.DIL, x_yari):
        govde += Pos(x0, y0, dil_z0) * Box(p.DIL, p.WALL, dil_h, align=MIN3)
    if p.YAN_KILIT:
        govde -= yan_oluk(z0, z0 + h)
    return govde
