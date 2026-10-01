"""Panel dili ile köşe/kıskaç kanalı ve karo oluğu arasındaki ortak kesit.

Yerel çerçeve: y = 0 kutunun nominal dış yüzü, +y kutunun içi.
"""
from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3


def panel_y() -> tuple[float, float]:
    y0 = p.GAP + p.LIP
    return (y0, y0 + p.WALL)


def yuva_y() -> tuple[float, float]:
    y0, y1 = panel_y()
    return (y0 - p.FIT, y1 + p.FIT)


def yuva(x0: float, x1: float, z0: float, z1: float) -> Part:
    y0, y1 = yuva_y()
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


def anahtar(z0: float, z1: float) -> Part:
    """Panel alt dilindeki hata önleyici çıkıntı (panel çerçevesi)."""
    _, y1 = panel_y()
    return Pos(p.ANAHTAR_X - p.ANAHTAR_W / 2, y1, z0) * Box(p.ANAHTAR_W, p.ANAHTAR_T, z1 - z0, align=MIN3)


def anahtar_cebi(z0: float, z1: float) -> Part:
    """Anahtarın oturduğu cep (panel çerçevesi); oluğun iç duvarına açılır."""
    _, y1 = panel_y()
    w = p.ANAHTAR_W + 2 * p.FIT
    return Pos(p.ANAHTAR_X - w / 2, y1, z0) * Box(w, p.ANAHTAR_T + p.FIT, z1 - z0, align=MIN3)
