"""Kapak mandalı: kapağın ön kenarında kayar sürgü, aşağı inen kanca çerçevedeki yuvaya girer.

Çerçeve: node orijini (güney kenar), z = 0 kutunun nominal üstü. Kilitliyken kanca başı
çerçevenin tutma çıkıntısının FIT altında; sürgü −x'e KAPAK_MANDAL_YOL kayınca kanca
giriş penceresinin altına gelir ve kapak açılabilir. Sürgüye bağlı dil kapağın ön yüzüne
uzanır; dışarıdan parmakla itilir.
"""
from functools import cache

from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3

_F = p.FIT
_C = p.P_XY / 2
_KAPAK_ALT = -p.GAP - p.KAPAK_H
_SY0, _SY1 = 7.0, 17.0           # sürgü
_KY0, _KY1 = 10.0, 14.0          # kanca
_S_L = 20.0                      # sürgü boyu
_K_W, _K_BAS = 4.0, 12.0         # kanca gövdesi ve başı (x)
_CIKINTI = 2.0                   # çerçevedeki tutma çıkıntısı kalınlığı
_BAS_H = 2.2


def _k(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


def _olculer():
    sx0 = _C - _S_L / 2
    kx0 = _C                                     # kilitli kanca gövdesi
    cikinti_alt = _KAPAK_ALT - _CIKINTI          # çerçeve üstü − çıkıntı
    bas_z1 = cikinti_alt - _F
    bas_z0 = bas_z1 - _BAS_H
    return sx0, kx0, cikinti_alt, bas_z0, bas_z1


@cache
def mandal() -> Part:
    sx0, kx0, _, bas_z0, bas_z1 = _olculer()
    surgu = _k(sx0, sx0 + _S_L, _SY0, _SY1, _KAPAK_ALT + 0.4, -p.GAP - 0.4)
    govde = _k(kx0, kx0 + _K_W, _KY0, _KY1, bas_z0, _KAPAK_ALT + 0.4 + 0.01)
    bas = _k(kx0, kx0 + _K_BAS, _KY0, _KY1, bas_z0, bas_z1)
    dil = _k(sx0 + _S_L - _K_W, sx0 + _S_L, p.GAP + 0.1, _SY0 + 0.01, -p.GAP - 3.2, -p.GAP - 1.2)
    return surgu + govde + bas + dil


def acik_mandal() -> Part:
    return Pos(-p.KAPAK_MANDAL_YOL, 0, 0) * mandal()


def kapak_cebi() -> Part:
    """Kapaktan çıkarılacak: sürgü cebi ve dil yolu (kilitli + açık konum)."""
    sx0, _, _, _, _ = _olculer()
    y = p.KAPAK_MANDAL_YOL
    cep = _k(sx0 - y - _F, sx0 + _S_L + _F, _SY0 - _F, _SY1 + _F, _KAPAK_ALT - 0.01, -p.GAP + 0.01)
    dil = _k(sx0 + _S_L - _K_W - y - _F, sx0 + _S_L + _F, p.GAP - 0.01, _SY0, -p.GAP - 3.2 - _F, -p.GAP - 1.2 + _F)
    return cep + dil


def cerceve_yuvasi() -> Part:
    """Çerçeveden çıkarılacak anahtar deliği: giriş penceresi + altında oda."""
    _, kx0, cikinti_alt, bas_z0, _ = _olculer()
    y = p.KAPAK_MANDAL_YOL
    y0, y1 = _KY0 - _F - 0.7, _KY1 + _F          # öne doğru pay: kapak açılırken kanca hafif öne kayar
    pencere = _k(kx0 - y - _F, kx0 + _K_W + _F, y0, y1, cikinti_alt, _KAPAK_ALT + 0.01)
    pencere += _k(kx0 - y - _F, kx0 - y + _K_BAS + _F, y0, y1, cikinti_alt, _KAPAK_ALT + 0.01)
    oda = _k(kx0 - y - _F, kx0 + _K_BAS + _F, y0, y1, bas_z0 - _F, cikinti_alt)
    return pencere + oda
