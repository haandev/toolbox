"""Tavan modülü (1×1, 2×1, 1×2, 2×2): üst çerçeve + menteşeli kapak; kutular bu modüllerle döşenir.

Yerel çerçeve: x, y kutu ızgarası (0 … nx·P_XY), z = 0 kutunun nominal üstü.
Çerçeve (z −T … −KAPAK_H−GAP): kenar halkası, altta panel oluğu, köşe/kıskaç vida delikleri,
anahtar cepleri, ön kenarda kapak mandalı yuvaları, arka kenarda menteşe boğumları ve pim.
Kapak (z −KAPAK_H−GAP … −GAP): tam üst yüzey; altta güverte, üstte kaburgalar; T raylar,
gömme kulp oyuğu/teknesi, mafsal blokları, mandal cepleri, kapak boğumları. Kapak arka üst
kenardaki eksen etrafında açılır.
"""
from functools import cache

from build123d import Align, Box, Cylinder, Part, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import anahtar_cebi, yuva
from kutu.lib.papyon import yarim_yuva
from kutu.parts.karo import delik_noktalari
from kutu.parts.kulp import EKSEN_Y, KULP_Z0, MAFSAL_Z, TUTMA_Y, kulp_x0
from kutu.parts.kapak_mandal import cerceve_yuvasi, kapak_cebi
from kutu.parts.t_kanal import RAY_XLER, ray


def kulp_boyu(nx: int) -> int:
    """Modülün kulp boyu: 1×1 → 1×, 2×1 ve 2×2 → 2×."""
    return min(nx, 2)


def tavan_modulleri(nx: int, ny: int) -> list[tuple[int, int, int, int]]:
    """Kutunun tavanını 2×2, 2×1, 1×2, 1×1 modüllerle döşer: [(i0, j0, mx, my)].

    Satır satır, önce 2×2, sonra 2×1 (genişlik), sonra 1×2 (derinlik), kalan yerlere 1×1.
    """
    dolu: set[tuple[int, int]] = set()
    out = []
    for j in range(ny):
        for i in range(nx):
            if (i, j) in dolu:
                continue
            for mx, my in ((2, 2), (2, 1), (1, 2), (1, 1)):
                hucre = {(i + a, j + b) for a in range(mx) for b in range(my)}
                if i + mx <= nx and j + my <= ny and not (hucre & dolu):
                    dolu |= hucre
                    out.append((i, j, mx, my))
                    break
    return out


def kulp_yeri(nx: int, ny: int) -> tuple[float, float]:
    """Kulp bölgesinin başlangıç x'i ve orta çizgisinin y'si (kutu çerçevesi)."""
    n = kulp_boyu(nx)
    return (nx * p.P_XY - n * p.P_XY) / 2, ny * p.P_XY / 2


def _kutu(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


def _duvar_yerlesimleri(W: float, D: float, nx: int, ny: int):
    """(yerleşim, baş aşağı mı) — batı ve kuzey panelleri baş aşağı takılır."""
    c = p.P_XY / 2
    for i in range(nx):
        yield Pos(c + i * p.P_XY, 0, 0), False
        yield Pos(c + i * p.P_XY, D, 0) * Rot(0, 0, 180), True
    for j in range(ny):
        yield Pos(0, c + j * p.P_XY, 0) * Rot(0, 0, -90), True
        yield Pos(W, c + j * p.P_XY, 0) * Rot(0, 0, 90), False


_KAPAK_ALT = -p.GAP - p.KAPAK_H
MODUL_KAM_Z0 = -p.T                                   # modüller arası kam alttan takılır
MODUL_ARASI = 2 * p.GAP                               # iki modül çerçevesi arası boşluk


def modul_kam_yuvalari(mx: int, my: int) -> Part:
    """Modül çerçevesinin dört kenarında, her node kenarında YUVA_U'da alttan yarım kam yuvaları."""
    W, D = mx * p.P_XY, my * p.P_XY
    z0, z1 = MODUL_KAM_Z0 - 0.01, MODUL_KAM_Z0 + p.PAPYON_H + p.FIT
    yuvalar = []
    for i in range(mx):
        for u in p.YUVA_U:
            x = i * p.P_XY + u
            yuvalar.append(yarim_yuva(x, MODUL_ARASI, z0, z1))                                 # güney
            yuvalar.append(Pos(0, D, 0) * Rot(0, 0, 180) * yarim_yuva(-x, MODUL_ARASI, z0, z1))  # kuzey
    for j in range(my):
        for u in p.YUVA_U:
            y = j * p.P_XY + u
            yuvalar.append(Rot(0, 0, -90) * yarim_yuva(-y, MODUL_ARASI, z0, z1))               # batı
            yuvalar.append(Pos(W, 0, 0) * Rot(0, 0, 90) * yarim_yuva(y, MODUL_ARASI, z0, z1))  # doğu
    tum = yuvalar[0]
    for y_ in yuvalar[1:]:
        tum += y_
    return tum


def _duvar_yerlesimleri(W: float, D: float, nx: int, ny: int):
    """(yerleşim, baş aşağı mı) — batı ve kuzey panelleri baş aşağı takılır."""
    c = p.P_XY / 2
    for i in range(nx):
        yield Pos(c + i * p.P_XY, 0, 0), False
        yield Pos(c + i * p.P_XY, D, 0) * Rot(0, 0, 180), True
    for j in range(ny):
        yield Pos(0, c + j * p.P_XY, 0) * Rot(0, 0, -90), True
        yield Pos(W, c + j * p.P_XY, 0) * Rot(0, 0, 90), False


_KAPAK_ALT = -p.GAP - p.KAPAK_H
MODUL_KAM_Z0 = -p.T                                   # modüller arası kam alttan takılır
MODUL_ARASI = 2 * p.GAP                               # iki modül çerçevesi arası boşluk


def modul_kam_yuvalari(mx: int, my: int) -> Part:
    """Modül çerçevesinin dört kenarında, her node kenarında YUVA_U'da alttan yarım kam yuvaları."""
    W, D = mx * p.P_XY, my * p.P_XY
    z0, z1 = MODUL_KAM_Z0 - 0.01, MODUL_KAM_Z0 + p.PAPYON_H + p.FIT
    tum = None
    for kenar_boyu, adet, yer in ((W, mx, lambda u: Pos(0, 0, 0)),):
        pass
    def ekle(parca):
        nonlocal tum
        tum = parca if tum is None else tum + parca
    for i in range(mx):
        for u in p.YUVA_U:
            x = i * p.P_XY + u
            ekle(yarim_yuva(x, MODUL_ARASI, z0, z1))                                   # güney
            ekle(Pos(0, D, 0) * Rot(180, 0, 0) * Pos(0, 0, 0) * _ayna_z(yarim_yuva(x, MODUL_ARASI, z0, z1)))
    for j in range(my):
        for u in p.YUVA_U:
            y = j * p.P_XY + u
            ekle(Rot(0, 0, -90) * yarim_yuva(-y, MODUL_ARASI, z0, z1))                 # batı (+x'e açılır)
            ekle(Pos(W, 0, 0) * Rot(0, 0, 90) * yarim_yuva(y, MODUL_ARASI, z0, z1))   # doğu
    return tum


def _ayna_z(parca: Part) -> Part:
    """Rot(180,0,0) z'yi de çevirdiği için kuzey yuvasında z aralığını geri getirir."""
    b = parca.bounding_box()
    return Pos(0, 0, -(b.min.Z + b.max.Z)) * parca


def mentese_ekseni(ny: int) -> tuple[float, float]:
    """Menteşe ekseninin (y, z)'si; eksen x boyunca."""
    return ny * p.P_XY - p.GAP - p.MENTESE_R, -p.GAP - p.MENTESE_R


def _bogumlar(nx: int):
    """[(x0, x1, çerçeve mi)] — iki uçta çerçeve boğumu, aralarda FIT."""
    x0, x1 = p.K, nx * p.P_XY - p.K
    n = max(3, int((x1 - x0) // p.MENTESE_BOGUM))
    if n % 2 == 0:
        n -= 1
    L = (x1 - x0) / n
    out = []
    for i in range(n):
        a = x0 + i * L + (p.FIT / 2 if i > 0 else 0)
        b = x0 + (i + 1) * L - (p.FIT / 2 if i < n - 1 else 0)
        out.append((a, b, i % 2 == 0))
    return out


def _silindir_x(x0: float, x1: float, y: float, z: float, r: float) -> Part:
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0)


@cache
def cerceve(nx: int, ny: int) -> Part:
    g, W, D = p.GAP, nx * p.P_XY, ny * p.P_XY
    alt, ust = -p.T, _KAPAK_ALT
    t = _kutu(g, W - g, g, D - g, alt, ust)
    t -= _kutu(p.K, W - p.K, p.K, D - p.K, alt - 1, ust + 1)                # iç açıklık

    for yer, bas_asagi in _duvar_yerlesimleri(W, D, nx, ny):
        t -= yer * yuva(-p.P_XY / 2, p.P_XY / 2, alt, alt + p.DIL_V + p.FIT)
        if bas_asagi:                    # baş aşağı panelin anahtarı üstte, x = −ANAHTAR_X
            t -= yer * anahtar_cebi(alt, alt + p.DIL_V + p.FIT, x=-p.ANAHTAR_X)

    for i in range(nx):                  # köşe ve kıskaç vida delikleri (dış kenara yakın olanlar)
        for j in range(ny):
            for hx, hy in delik_noktalari():
                x, y = hx + i * p.P_XY, hy + j * p.P_XY
                if min(x, y, W - x, D - y) < p.K:
                    t -= Pos(x, y, alt) * Cylinder(p.GECIS_DELIK / 2, p.T,
                                                   align=(Align.CENTER, Align.CENTER, Align.MIN))

    for i in range(nx):                  # ön kenarda kapak mandalı yuvaları
        t -= Pos(i * p.P_XY, 0, 0) * cerceve_yuvasi()
    t -= modul_kam_yuvalari(nx, ny)      # modüller arası kam yuvaları (alttan)

    ya, za = mentese_ekseni(ny)          # arka kenarda çerçeve boğumları + pim
    for a, b, cerceve_mi in _bogumlar(nx):
        if cerceve_mi:
            t += _silindir_x(a, b, ya, za, p.MENTESE_R)
        else:                            # kapak boğumunun dönme alanı
            t -= _silindir_x(a - p.FIT / 2, b + p.FIT / 2, ya, za, p.MENTESE_R + p.FIT)
    t += _silindir_x(p.K, W - p.K, ya, za, p.MENTESE_PIM_R)
    return t


def _kapak_govde(nx: int, ny: int) -> Part:
    g, W, D = p.GAP, nx * p.P_XY, ny * p.P_XY
    alt, ust = _KAPAK_ALT, -g
    t = _kutu(g, W - g, g, D - g, alt, ust)
    t -= _kutu(g + p.WALL, W - g - p.WALL, g + p.WALL, D - g - p.WALL, alt + p.WALL, ust + 1)   # üstten cep
    x = p.K + p.KARO_RIB_ARALIK
    while x < W - p.K - 1e-6:
        t += _kutu(x - p.RIB / 2, x + p.RIB / 2, g, D - g, alt + p.WALL, ust)
        x += p.KARO_RIB_ARALIK
    y = p.K + p.KARO_RIB_ARALIK
    while y < D - p.K - 1e-6:
        t += _kutu(g, W - g, y - p.RIB / 2, y + p.RIB / 2, alt + p.WALL, ust)
        y += p.KARO_RIB_ARALIK
    for y0 in (p.K, D - p.K - p.RIB):    # ön ve arka kenar boyunca kaburga (mandal ve T ray için taşıyıcı)
        t += _kutu(g, W - g, y0, y0 + p.RIB, alt + p.WALL, ust)
    return t


def _t_raylar(nx: int, ny: int) -> Part:
    D = ny * p.P_XY
    tum = None
    for i in range(nx):
        for hx in RAY_XLER:
            r = ray(i * p.P_XY + hx, p.GAP, D - p.GAP)
            tum = r if tum is None else tum + r
    return tum


def _kulp_bolgeleri(nx: int, ny: int):
    """(oyuk, süpürme zarfı, mafsal blokları) — kutu çerçevesinde."""
    n = kulp_boyu(nx)
    xs, yc = kulp_yeri(nx, ny)
    x0 = xs + kulp_x0()
    x1 = xs + n * p.P_XY - kulp_x0()
    bx0, bx1 = x0 - p.FIT - p.MAFSAL_L, x1 + p.FIT + p.MAFSAL_L
    kilit = -p.GAP
    taban = kilit + KULP_Z0 - 1
    ey = yc + EKSEN_Y                                   # mafsal ekseni: modül orta çizgisi
    gy = yc + TUTMA_Y                                   # katlı tutma yeri
    ey0 = ey - max(p.MAFSAL_W, p.KULP_H) / 2 - 1      # açılırken kolun mafsal altına inen ucu dahil
    oyuk = (_kutu(x0 - 1, x1 + 1, gy - p.KULP_W / 2 - 1, gy + p.KULP_W / 2 + 1, taban, kilit + 1)
            + _kutu(bx0, x0 + p.KOL_T + 1, ey0, gy, taban, kilit + 1)
            + _kutu(x1 - p.KOL_T - 1, bx1, ey0, gy, taban, kilit + 1))
    zarf = _kutu(x0 - 1, x1 + 1, min(ey0, ey - p.KULP_W / 2 - 2), gy + p.KULP_W / 2 + 2, kilit, p.T_BAS_Z1 + 1)
    mz = kilit + MAFSAL_Z
    bloklar = None
    for bx in (bx0, x1 + p.FIT):
        blok = _kutu(bx, bx + p.MAFSAL_L, ey - p.MAFSAL_W / 2, ey + p.MAFSAL_W / 2, taban, kilit - 1)
        blok -= Pos(bx + p.MAFSAL_L / 2, ey, mz) * Rot(0, 90, 0) * Cylinder(p.PIM_D / 2 + p.FIT, p.MAFSAL_L + 1)
        bloklar = blok if bloklar is None else bloklar + blok
    return oyuk, zarf, bloklar


@cache
def kapak(nx: int, ny: int) -> Part:
    oyuk, zarf, bloklar = _kulp_bolgeleri(nx, ny)
    # tekne: oyuğun WALL kalınlığında kabuğu, çerçeve açıklığından kutunun içine sarkar
    tekne = None
    for parca in oyuk.solids():
        b = parca.bounding_box()
        kabuk = _kutu(b.min.X - p.WALL, b.max.X + p.WALL, b.min.Y - p.WALL, b.max.Y + p.WALL,
                      b.min.Z - p.WALL, -p.GAP)
        tekne = kabuk if tekne is None else tekne + kabuk
    t = _kapak_govde(nx, ny) + tekne - oyuk + bloklar
    t += _t_raylar(nx, ny) - zarf - oyuk    # raylar kulbun süpürme bölgesinde kesik
    for i in range(nx):                     # mandal cepleri
        t -= Pos(i * p.P_XY, 0, 0) * kapak_cebi()

    # menteşe: eksenin arkasında yalnız kapak boğumları; çerçeve boğumlarının çevresi boş
    W = nx * p.P_XY
    ya, za = mentese_ekseni(ny)
    t -= _kutu(-1, W + 1, ya, ny * p.P_XY + 1, _KAPAK_ALT - 1, 1)
    for a, b, cerceve_mi in _bogumlar(nx):
        if cerceve_mi:
            t -= _silindir_x(a - p.FIT / 2, b + p.FIT / 2, ya, za, p.MENTESE_R + p.FIT)
        else:
            t += _silindir_x(a, b, ya, za, p.MENTESE_R)
    t -= _silindir_x(-1, W + 1, ya, za, p.MENTESE_PIM_R + p.FIT)          # pim deliği
    return t


def tavan(nx: int, ny: int) -> Part:
    """Kapalı tavan (çerçeve + kapak) — eski arayüz için."""
    return cerceve(nx, ny) + kapak(nx, ny)
