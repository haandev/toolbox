"""Papyon (kırlangıç) kam: iki parçayı ek yerinde birleştiren bağlantı.

Ek yeri çizgisi y = 0; kam x = 0 merkezli, y = −H … H; boynu ek yerinde (PAPYON_A), uçları
geniş (PAPYON_B). Yarım yuva, ek yerinin +y tarafındaki parçaya açılır.
"""
from build123d import Part, Polygon, Pos, extrude

from kutu import params as p


def prizma(nokta: list[tuple[float, float]], z0: float, z1: float) -> Part:
    """XY poligonunu z0 … z1 arasında uzatır (köşe sırası ne olursa olsun yukarı doğru)."""
    alan = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(nokta, nokta[1:] + nokta[:1]))
    if alan < 0:
        nokta = list(reversed(nokta))
    return Pos(0, 0, z0) * extrude(Polygon(*nokta, align=None), amount=z1 - z0)


def yari_boy(bosluk: float) -> float:
    """Ek yeri boşluğu (iki parça arası) verildiğinde kamın yarı boyu."""
    return bosluk / 2 + p.PAPYON_L


def papyon(bosluk: float) -> Part:
    """Kam (z = 0 … PAPYON_H − FIT)."""
    a, b, H = p.PAPYON_A / 2, p.PAPYON_B / 2, yari_boy(bosluk)
    return prizma([(-a, 0), (-b, H), (b, H), (a, 0), (b, -H), (-b, -H)], 0, p.PAPYON_H - p.FIT)


def yarim_yuva(u: float, bosluk: float, z0: float, z1: float) -> Part:
    """+y tarafındaki parçaya açılan yarım yuva (x = u'da, FIT büyütülmüş)."""
    f = p.FIT
    a, b, H = p.PAPYON_A / 2 + f, p.PAPYON_B / 2 + f, yari_boy(bosluk) + f
    return prizma([(u - a, -0.01), (u + a, -0.01), (u + b, H), (u - b, H)], z0, z1)
