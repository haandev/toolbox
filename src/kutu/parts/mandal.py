"""Dikey çekme mandalı.

Tavanın kenar çerçevesinin iç kısmındaki cepte kayan sürgü; sürgüden yukarı çıkan kanca,
üstteki kutunun taban karosundaki anahtar deliği biçimli yuvaya girer. Sürgü +x'e
MANDAL_YOL kayınca kanca başı yuvadaki çıkıntının üstüne geçer (kilitli). Sürgüye bağlı
dil, panel oluğunun üstünden kutu yüzüne uzanır; dışarıdan parmakla itilir.

Çerçeve: güney kenar, node orijini; x node boyunca, y kutu yüzünden içe, z = 0 kutunun
nominal üstü (= üstteki kutunun taban yerel z'si). Kuzey kenar node merkezi etrafında 180°.
"""
from functools import cache

from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3

_F = p.FIT


def _k(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


def _olculer():
    sx0 = p.P_XY / 2 + p.MANDAL_X - p.MANDAL_L / 2      # sürgü başı (kilitli)
    sx1 = sx0 + p.MANDAL_L
    kx0 = sx0 + p.MANDAL_YOL                            # kanca gövdesi (kilitli)
    kilit = -p.GAP
    return sx0, sx1, kx0, kilit


@cache
def mandal() -> Part:
    """Kilitli konumdaki mandal (sürgü + kanca + dil)."""
    sx0, sx1, kx0, kilit = _olculer()
    tavan_ici = kilit - 1.0                              # sürgü üstü, tavan kabuğunun altında
    surgu = _k(sx0, sx1, p.MANDAL_Y0, p.MANDAL_Y1, tavan_ici - 6, tavan_ici)
    bas_z0 = p.CIKINTI_H + _F
    bas_z1 = bas_z0 + p.KANCA_BAS_H
    govde = _k(kx0, kx0 + p.KANCA_W, p.KANCA_Y0, p.KANCA_Y1, tavan_ici, bas_z1)
    bas = _k(kx0, kx0 + p.KANCA_BAS, p.KANCA_Y0, p.KANCA_Y1, bas_z0, bas_z1)
    dil_z0 = -p.T + p.DIL + p.FIT + 0.2                  # tavan panel oluğunun üstünden geçer
    dil = _k(sx1 - p.KANCA_W, sx1, p.GAP + 0.1, p.MANDAL_Y0, dil_z0, tavan_ici)
    return surgu + govde + bas + dil


def acik_mandal() -> Part:
    return Pos(-p.MANDAL_YOL, 0, 0) * mandal()


def tavan_cebi() -> Part:
    """Tavandan çıkarılacak hacim: sürgü cebi, kanca yolu, dil yolu (açık + kilitli konumlar)."""
    sx0, sx1, kx0, kilit = _olculer()
    tavan_ici = kilit - 1.0
    y = p.MANDAL_YOL
    cep = _k(sx0 - y - _F, sx1 + _F, p.MANDAL_Y0 - _F, p.MANDAL_Y1 + _F, tavan_ici - 6 - _F, tavan_ici + _F)
    yol = _k(kx0 - y - _F, kx0 + p.KANCA_W + _F, p.KANCA_Y0 - _F, p.KANCA_Y1 + _F, tavan_ici, kilit + 0.01)
    dil_z0 = -p.T + p.DIL + p.FIT + 0.2
    dil = _k(sx1 - p.KANCA_W - y - _F, sx1 + _F, p.GAP - 0.01, p.MANDAL_Y0, dil_z0 - _F, tavan_ici)
    return cep + yol + dil


def taban_yuvasi() -> Part:
    """Üst kutunun taban karosuna açılan anahtar deliği (güney kenar, taban yerel z)."""
    _, _, kx0, _ = _olculer()
    y = p.MANDAL_YOL
    pencere_x1 = kx0 + p.KANCA_W + _F                    # kilitli gövde pencerede kalır
    giris = _k(kx0 - y - _F, max(pencere_x1, kx0 - y + p.KANCA_BAS + _F), p.KANCA_Y0 - _F, p.KANCA_Y1 + _F,
               -0.01, p.CIKINTI_H)
    oda = _k(kx0 - y - _F, kx0 + p.KANCA_BAS + _F, p.KANCA_Y0 - _F, p.KANCA_Y1 + _F,
             p.CIKINTI_H, p.CIKINTI_H + _F + p.KANCA_BAS_H + _F)
    return giris + oda
