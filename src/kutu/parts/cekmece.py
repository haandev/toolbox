"""Çekmece ve kat arası raf.

Çekmece (node çerçevesi: x 0 … P_XY, y kutu ön yüzünden içe, z kutu çerçevesi): ön plaka
panelin yerini kapatır ve panel dış yüzüyle aynı hizadadır; arkasında tepsi. Ön plakanın
üst ortasında parmak girintisi. Tepsi tabanın / rafın üstünde FIT boşlukla kayar.
Raf (kutu çerçevesi): kat arasında yatay kıskaçların iç çıkıntılarına oturur; köşe ve
kıskaç izlerinde çentikli; altı kaburgalı. Kutu boyuna göre tek parça.

Durdurucu: taban/raf üstündeki çıkıntı, tepsi altındaki önden açık oluğun içinde kayar;
oluk bitince çekmece CEKMECE_YOL'da durur (çıkarmak için önü kaldırılır). Oluk tavanındaki
tümsek kapalı tutucudur.
"""
from functools import cache

from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y


def _k(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


@cache
def cekmece(plaka_z0: float, plaka_z1: float, tepsi_z0: float, tepsi_z1: float) -> Part:
    x0, x1 = p.K + p.CEKMECE_B, p.P_XY - p.K - p.CEKMECE_B
    y0, y1 = panel_y()
    arka = p.P_XY - (p.GAP + p.LIP + p.WALL + p.RIB_D) - p.FIT    # arka panel kaburgalarının önü
    plaka = _k(x0, x1, y0, y1, plaka_z0, plaka_z1)
    c = p.P_XY / 2
    plaka -= _k(c - p.CEKMECE_TUTAMAK_W / 2, c + p.CEKMECE_TUTAMAK_W / 2, y0 - 1, y1 + 1,
                plaka_z1 - p.CEKMECE_TUTAMAK_H, plaka_z1 + 1)
    arka = min(arka, p.P_XY - p.DURDURUCU_Y0 - p.DURDURUCU_L - p.FIT)   # arka kenar çıkıntısının önü
    w = p.WALL
    tepsi = _k(x0, x1, y1, arka, tepsi_z0, tepsi_z1)
    tepsi -= _k(x0 + w, x1 - w, y1, arka - w, tepsi_z0 + w, tepsi_z1 + 1)

    # durdurucu oluğu (alttan) + üstünde tünel; oluk sonu durdurma yüzü
    zemin = tepsi_z0 - p.FIT
    og = p.DURDURUCU_W / 2 + p.FIT
    oluk_tavan = zemin + p.DURDURUCU_H + p.FIT
    oluk_son = p.DURDURUCU_Y0 + p.DURDURUCU_L + p.CEKMECE_YOL
    tepsi += _k(c - og - w, c + og + w, y1, oluk_son + w, tepsi_z0 + w - 0.01, oluk_tavan + w)
    tepsi -= _k(c - og, c + og, y1 - 0.01, oluk_son, tepsi_z0 - 0.01, oluk_tavan)
    # kapalı tutucu tümseği: kapalıyken çıkıntının hemen önünde
    t0 = p.DURDURUCU_Y0 + p.DURDURUCU_L + 0.3
    tepsi += _k(c - og, c + og, t0, t0 + 2, oluk_tavan - p.TUTUCU_TUMSEK, oluk_tavan)
    return plaka + tepsi


def durdurucu(x_merkez: float, zemin: float) -> Part:
    """Ön kenardaki durdurucu çıkıntısı (zemin üstünde)."""
    w = p.DURDURUCU_W / 2
    return _k(x_merkez - w, x_merkez + w, p.DURDURUCU_Y0, p.DURDURUCU_Y0 + p.DURDURUCU_L,
              zemin, zemin + p.DURDURUCU_H)


@cache
def raf(nx: int, ny: int, kat: int) -> Part:
    """kat ile kat+1 arasındaki raf (kutu çerçevesinde)."""
    W, D = nx * p.P_XY, ny * p.P_XY
    z0 = kat * p.P_Z + p.T + p.H + 2 * p.T
    e = p.RAF_KENAR
    r = _k(e, W - e, e, D - e, z0, z0 + p.WALL)
    k = p.K + p.FIT
    for x in (0, W):                       # köşe izleri
        for y in (0, D):
            r -= _k(x - k, x + k, y - k, y + k, z0 - 1, z0 + p.WALL + 1)
    for i in range(1, nx):                 # ön/arka kıskaç izleri
        for y in (0, D):
            r -= _k(i * p.P_XY - k, i * p.P_XY + k, y - k, y + k, z0 - 1, z0 + p.WALL + 1)
    for j in range(1, ny):                 # yan kıskaç izleri
        for x in (0, W):
            r -= _k(x - k, x + k, j * p.P_XY - k, j * p.P_XY + k, z0 - 1, z0 + p.WALL + 1)

    # alt kaburgalar: yatay kıskaçların iç yüzünden içeride
    a = p.K + p.FIT
    x = p.K + p.KARO_RIB_ARALIK
    while x < W - p.K - 1e-6:
        r += _k(x - p.RIB / 2, x + p.RIB / 2, a, D - a, z0 - p.RAF_RIB_D, z0)
        x += p.KARO_RIB_ARALIK
    y = p.K + p.KARO_RIB_ARALIK
    while y < D - p.K - 1e-6:
        r += _k(a, W - a, y - p.RIB / 2, y + p.RIB / 2, z0 - p.RAF_RIB_D, z0)
        y += p.KARO_RIB_ARALIK

    for i in range(nx):                    # üst kat çekmecelerinin durdurucuları (ön kenar)
        r += durdurucu(i * p.P_XY + p.P_XY / 2, z0 + p.WALL)
    return r


def raf_sehimi(yuk_kg: float, nx: int, ny: int, kaburga: bool = True) -> float:
    """Rafın yayılı yük altında en büyük sehimi (mm).

    Model: kaburgalar kısa açıklık boyunca basit mesnetli kirişler; her kaburga, aralığı
    genişliğinde raf plakasıyla T kesit oluşturur ve kendi şeridinin yükünü taşır.
    """
    s = p.KARO_RIB_ARALIK / 1000
    t = p.WALL / 1000
    L = (min(nx, ny) * p.P_XY - 2 * p.K) / 1000
    alan = ((nx * p.P_XY - 2 * p.K) / 1000) * ((ny * p.P_XY - 2 * p.K) / 1000)
    q = yuk_kg * 9.81 / alan * s                       # kaburga başına çizgisel yük (N/m)
    if kaburga:
        bw, d = p.RIB / 1000, p.RAF_RIB_D / 1000
        a1, a2 = s * t, bw * d
        yc = (a1 * t / 2 + a2 * (t + d / 2)) / (a1 + a2)
        I = (s * t**3 / 12 + a1 * (yc - t / 2) ** 2 + bw * d**3 / 12 + a2 * (t + d / 2 - yc) ** 2)
    else:
        I = s * t**3 / 12
    return 5 * q * L**4 / (384 * p.MALZEME_E * I) * 1000
