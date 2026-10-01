"""Duvar paneli: düz deri + iç kaburgalar; dört kenarda dil."""
from functools import cache

from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y
from kutu.lib.kilit_yeri import panel_bolgesi


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

    return deri + kaburga
