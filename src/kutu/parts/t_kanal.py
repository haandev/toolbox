"""T kanal: dikey kilit, öne kayarak takma/çıkarma.

Tavanın ön ve arka kenar çerçevesinde sabit T kancalar; üstteki kutunun taban karosunda,
her kenarda kenar ortasından T_KANCA_X'te önü ve arkası açık T kanal (boyun + baş) ve
−T_KANCA_X'te karşı kenarın kancası için düz geçit. Kanca başı kanalın tutma çıkıntısının
FIT üstündedir: üst kutu kalkamaz, öne–arkaya kayar.

Çerçeve: güney kenar, node orijini; z = 0 kutunun nominal üstü (= üst taban yerel z).
"""
from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3

_F = p.FIT
_C = p.P_XY / 2


def _k(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


def kanca() -> Part:
    hx = _C + p.T_KANCA_X
    y0, y1 = p.T_KANCA_Y0, p.T_KANCA_Y1
    boyun = _k(hx - p.T_BOYUN_W / 2, hx + p.T_BOYUN_W / 2, y0, y1, -p.GAP - 1.0, p.T_BAS_Z0 + 0.01)
    bas = _k(hx - p.T_BAS_W / 2, hx + p.T_BAS_W / 2, y0, y1, p.T_BAS_Z0, p.T_BAS_Z1)
    return boyun + bas


def taban_kanali() -> Part:
    """Taban karosundan çıkarılacak hacim (güney kenar): T kanal + karşı kancanın geçidi + kaburga şeritleri."""
    hx, gx = _C + p.T_KANCA_X, _C - p.T_KANCA_X
    bw, nw = p.T_BAS_W / 2 + _F, p.T_BOYUN_W / 2 + _F
    alt = p.GAP - 0.01
    y0, y1 = alt, p.K + 0.01
    t = (_k(hx - nw, hx + nw, y0, y1, alt, p.T_BOYUN_Z1)
         + _k(hx - bw, hx + bw, y0, y1, p.T_BOYUN_Z1, p.T_KANAL_Z1))
    gecit = _k(gx - bw, gx + bw, y0, y1, alt, p.T_KANAL_Z1)
    # cebin içinde kancaların ön–arka yolu: kaburgalar kırpılır
    yol = (_k(hx - bw, hx + bw, p.K, p.P_XY - p.K, alt, p.T_KANAL_Z1)
           + _k(gx - bw, gx + bw, p.K, p.P_XY - p.K, alt, p.T_KANAL_Z1))
    return t + gecit + yol
