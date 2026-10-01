"""Duvar paneli: düz deri + iç kaburgalar; dört kenarda dil."""
from functools import cache

from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import anahtar, panel_y
from kutu.lib import yan_ray
from kutu.lib.kilit_yeri import panel_bolgesi


@cache
def panel() -> Part:
    y0, y_ic = panel_y()
    deri = Pos(-p.PANEL_L / 2, y0, p.T - p.DIL_V) * Box(p.PANEL_L, p.WALL, p.PANEL_H, align=MIN3)

    # kaburgalar yalnızca görünür açıklıkta (kanal/oluk içine girmez), 1 mm pay
    z0, z1 = p.T + 1, p.T + p.H - 1
    x_yari = p.U / 2 - 1
    kaburga = Pos(-x_yari, y_ic, p.T + p.H / 2 - p.RIB / 2) * Box(2 * x_yari, p.RIB_D, p.RIB, align=MIN3)
    for x in p.PANEL_KABURGA_X:
        kaburga += Pos(x - p.RIB / 2, y_ic, z0) * Box(p.RIB, p.RIB_D, z1 - z0, align=MIN3)
    kaburga -= panel_bolgesi()

    # hata önleyici anahtar yalnız alt dilde: baş aşağı ya da içi dışına takılamaz
    govde = deri + kaburga + anahtar(p.T - p.DIL_V, p.T)
    if p.YAN_KILIT:
        govde = _yan_kilit(govde)
    return _tutma_girintisi(govde)


def _tutma_girintisi(govde: Part) -> Part:
    """Parmak açıklığı + deri arkasında yukarı uzanan cep; parmaklar derinin arkasına takılır."""
    _, y_ic = panel_y()
    w, z0 = p.TUTMA_W / 2, p.TUTMA_Z0
    kabuk = Pos(-w - p.WALL, y_ic, z0 - p.WALL) * Box(
        p.TUTMA_W + 2 * p.WALL, p.TUTMA_DERIN + p.WALL, p.TUTMA_H + 2 * p.WALL, align=MIN3)
    cep = Pos(-w, y_ic, z0) * Box(p.TUTMA_W, p.TUTMA_DERIN, p.TUTMA_H, align=MIN3)
    acik = Pos(-w, p.GAP - 0.01, z0) * Box(p.TUTMA_W, y_ic - p.GAP + 0.02, p.TUTMA_ACIK_H, align=MIN3)
    return govde + kabuk - cep - acik


def _yan_kilit(govde: Part) -> Part:
    """Yatay yan raylar: v₁'de dil, v₂'de oluk; görünür açıklık boyunca.

    Batı ve kuzey yüzlerinde panel baş aşağı takılır (montaj), böylece dil v₂'ye geçer ve
    komşunun v₂ oluğuna girer. Komşu kutu ray boyunca öne/arkaya kayabilir.
    """
    u = p.U / 2 - p.FIT                  # şerit ve dil köşe/kıskaç yüzlerine değmez
    L = p.PANEL_L / 2 + 0.01             # oluk, köşe kanalına giren yan diller dahil panelin tam boyunca
    return govde + yan_ray.serit(-u, u) + yan_ray.dil(-u, u) - yan_ray.oluk(-L, L, p.RAY_V2)
