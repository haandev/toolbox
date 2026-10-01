"""Vida kulesi: seri üretimde plastik vida, prototipte heat-set insert."""
from build123d import Align, Cylinder, Part

from kutu import params as p

_ALT = (Align.CENTER, Align.CENTER, Align.MIN)


def delik_capi() -> float:
    return p.INSERT_DELIK if p.PROTO else p.KULE_DELIK


def kule(boy: float) -> Part:
    """z=0'dan +z'ye uzanan kule; delik z=0'da açık, üstte WALL kadar kör."""
    dis = Cylinder(p.KULE_OD / 2, boy, align=_ALT)
    delik = Cylinder(delik_capi() / 2, boy - p.WALL, align=_ALT)
    return dis - delik
