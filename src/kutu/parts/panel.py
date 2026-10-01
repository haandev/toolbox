"""Duvar paneli: düz deri + iç kaburgalar; dört kenarda dil."""
from functools import cache

from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y
from kutu.lib.kilit_yeri import panel_bolgesi, yan_oluk


@cache
def panel() -> Part:
    y0, y_ic = panel_y()
    deri = Pos(-p.PANEL_L / 2, y0, p.T - p.DIL) * Box(p.PANEL_L, p.WALL, p.PANEL_H, align=MIN3)

    # kaburgalar yalnızca görünür açıklıkta (kanal/oluk içine girmez), 1 mm pay
    z0, z1 = p.T + 1, p.T + p.H - 1
    x_yari = p.U / 2 - 1
    kaburga = Pos(-x_yari, y_ic, p.T + p.H / 2 - p.RIB / 2) * Box(2 * x_yari, p.RIB_D, p.RIB, align=MIN3)
    for x in p.PANEL_KABURGA_X:
        kaburga += Pos(x - p.RIB / 2, y_ic, z0) * Box(p.RIB, p.RIB_D, z1 - z0, align=MIN3)
    kaburga -= panel_bolgesi()

    govde = deri + kaburga
    if p.YAN_KILIT:
        govde = _yan_kilit(govde)
    return govde


def _yan_kilit(govde: Part) -> Part:
    """Kilit bölgesinde dış yüze ped + dikey dil (-x) ve dikey oluk (+x).

    Ters çevrilen komşu panelin dili bu oluğa denk gelir (cinsiyetsiz); dil ve oluk
    dikey uzandığı için kutu yukarıdan indirilirken kayarak geçer.
    """
    y0, y_ic = panel_y()
    z0 = p.T + (p.H - p.KILIT_H) / 2
    ped = Pos(-p.KILIT_W / 2, p.GAP, z0) * Box(p.KILIT_W, y0 - p.GAP, p.KILIT_H, align=MIN3)
    dil = Pos(-p.YAN_KILIT_X - p.YAN_DIL_W / 2, p.GAP - p.YAN_DIL_H, z0) * Box(
        p.YAN_DIL_W, p.YAN_DIL_H, p.KILIT_H, align=MIN3)
    # oluk boydan boya açık: komşu kutu yukarıdan indirilirken dili hiçbir katta takılmaz;
    # kutunun yüksekliğini dikey istif belirler
    destek_w = p.YAN_DIL_W + 2 * p.FIT + 2 * p.WALL
    destek = Pos(p.YAN_KILIT_X - destek_w / 2, y_ic, z0) * Box(destek_w, p.WALL, p.T + p.H - 1 - z0, align=MIN3)
    return govde + ped + dil + destek - yan_oluk(p.T - p.DIL, p.T + p.H + p.DIL)
