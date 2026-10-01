"""Boydan boya T ray: dikey kilit ve yan hizalama, öne kayarak takma/çıkarma.

Tavanda her node sütununda, node merkezinden ±T_RAY_X'te ön–arka boyunca tam boy T ray
(boyun + baş). Taban karosunda aynı konumlarda iki yönde tam boy T kanal: çerçevede
oyuk olarak, iç cepte güverteden sarkan kanal duvarlarıyla. Kanca başı tutma çıkıntısının
FIT üstündedir: üst kutu kalkamaz, yana kayamaz, öne–arkaya kayar.

Çerçeve: node orijini; z = 0 kutunun nominal üstü (= üst taban yerel z).
""" 
from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3

_F = p.FIT
_C = p.P_XY / 2
RAY_XLER = (_C - p.T_RAY_X, _C + p.T_RAY_X)


def _k(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


def ray(hx: float, y0: float, y1: float) -> Part:
    """Tavan T rayı (x = hx, y0 … y1)."""
    boyun = _k(hx - p.T_BOYUN_W / 2, hx + p.T_BOYUN_W / 2, y0, y1, -p.GAP - 1.0, p.T_BAS_Z0 + 0.01)
    bas = _k(hx - p.T_BAS_W / 2, hx + p.T_BAS_W / 2, y0, y1, p.T_BAS_Z0, p.T_BAS_Z1)
    return boyun + bas


def _kanal_kesiti(hx: float, y0: float, y1: float) -> Part:
    bw, nw = p.T_BAS_W / 2 + _F, p.T_BOYUN_W / 2 + _F
    alt = p.GAP - 0.01
    return (_k(hx - nw, hx + nw, y0, y1, alt, p.T_BOYUN_Z1)
            + _k(hx - bw, hx + bw, y0, y1, p.T_BOYUN_Z1, p.T_KANAL_Z1))


def kanal_duvarlari() -> Part:
    """Taban cebinde y boyunca iki kanalın duvarları (güverteden kilit yüzüne sarkar)."""
    bw = p.T_BAS_W / 2 + _F + p.WALL
    tum = None
    for hx in RAY_XLER:
        d = _k(hx - bw, hx + bw, p.K, p.P_XY - p.K, p.GAP, p.T - p.WALL + 0.01)
        tum = d if tum is None else tum + d
    return tum


def kanal_kesimi() -> Part:
    """Taban karosundan çıkarılacak, y boyunca iki tam boy T kanal."""
    tum = None
    for hx in RAY_XLER:
        k = _kanal_kesiti(hx, -0.01, p.P_XY + 0.01)
        tum = k if tum is None else tum + k
    return tum


def node_kapasitesi(nx: int, ny: int) -> float:
    """Bir node'un (iki ray) taşıyabileceği dikey yük (N), kaba el hesabı.

    En zayıf eleman tabandaki tutma çıkıntıları: her ray iki çıkıntıya oturur; her çıkıntı
    (T_BAS_W − T_BOYUN_W)/2 çıkmalı ankastre konsol, yük çıkmanın ortasında,
    σ ≤ T_SIGMA_IZIN. Etkin boy: node derinliğinden kulp süpürme kesiği ve kanal
    kesişimleri düşülür. Kanca başı da aynı modelle kontrol edilir; küçüğü alınır.
    """
    c = (p.T_BAS_W - p.T_BOYUN_W) / 2 / 1000

    def mm_basina(t_mm: float) -> float:
        t = t_mm / 1000
        W = 1e-3 * t**2 / 6
        return 2 * p.T_SIGMA_IZIN * W / (c / 2)

    q = min(mm_basina(p.T_BOYUN_Z1 - p.GAP), mm_basina(p.T_BAS_Z1 - p.T_BAS_Z0))
    kesik = 2 * p.KULP_KOL + p.KULP_W                  # kulp süpürmesi (yaklaşık)
    kesisim = 2 * (p.T_BAS_W + 2 * _F)                 # dik kanallarla kesişimler
    etkin = p.P_XY - 2 * p.GAP - kesik - kesisim
    return 2 * etkin * q
