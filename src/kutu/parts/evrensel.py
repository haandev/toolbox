"""Evrensel tavan: tek tip çerçeve hücresi, tek tip kapak hücresi ve evrensel yuva ekleri.

Hücre çerçevesi: node orijini (x, y ∈ [0, P_XY]), z = 0 kutunun nominal üstü.
- Çerçeve hücresi (z −T … −GAP−KAPAK_H): halka, panel oluğu, 12 vida deliği, anahtar cebi;
  her kenarda YUVA_U ve YUVA_ORTA'da tam boy yarım papyon yuvaları.
- Kapak hücresi (z −GAP−KAPAK_H … −GAP): her kenardan KAPAK_ICERI içeride; altta güverte,
  kaburgalar, T raylar; orta kanal (y = 100) ve ön/arka kenar yarım kanalları (kaldırmalı kulp);
  her kenarda YUVA_U'da tam boy yarım yuvalar, orta çizgide YUVA_U'da tam yuvalar;
  menteşe boğumu ve pim boşlukları (dört kenarda — menteşe her kenarda olabilir).
- Ekler: kam (iki hücreyi kilitler), tapa (çevre kenarda yuvayı doldurur, panel oluğunu
  tamamlar), menteşe çerçeve/kapak ekleri, mandal eki.
Ekler güney kenar için tanımlıdır (arka kenar ekleri kuzey kenar); montaj döndürür.
"""
from functools import cache

from build123d import Align, Box, Cylinder, Part, Plane, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import anahtar_cebi, panel_y, yuva
from kutu.lib.papyon import prizma
from kutu.parts.karo import delik_noktalari
from kutu.parts.t_kanal import RAY_XLER, ray

_F = p.FIT
_C = p.P_XY / 2
_E = p.KAPAK_ICERI
ALT = -p.T                       # çerçeve altı
CUST = -p.GAP - p.KAPAK_H        # çerçeve üstü = kapak altı
KUST = -p.GAP                    # kapak üstü (kilit yüzü)
H = _E + p.PAPYON_L              # papyonun ek yeri çizgisinden ucuna
EY = p.P_XY - p.GAP - p.MENTESE_R   # arka kenar menteşe ekseni
EZ = -p.GAP - p.MENTESE_R
KAM_H = (CUST - ALT) - _F
KANAL_TABAN = KUST - p.KANAL_D


def _k(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


def _dort(parca: Part) -> Part:
    tum = None
    for aci in (0, 90, 180, 270):
        c = Pos(_C, _C, 0) * Rot(0, 0, aci) * Pos(-_C, -_C, 0) * parca
        tum = c if tum is None else tum + c
    return tum


def _kuzey(parca: Part) -> Part:
    """Güney kenar için tanımlı eki kuzey kenara (hücre merkezi etrafında 180°) taşır."""
    return Pos(_C, _C, 0) * Rot(0, 0, 180) * Pos(-_C, -_C, 0) * parca


def _yarim(u: float, z0: float, z1: float, pay: float, y0: float = -0.01) -> Part:
    """Güney kenarda x = u'da hücre içine doğru yarım papyon (pay: büyütme)."""
    a, b, h = p.PAPYON_A / 2 + pay, p.PAPYON_B / 2 + pay, H + pay
    a0 = a + (b - a) * max(y0, 0) / h
    return prizma([(u - a0, y0), (u + a0, y0), (u + b, h), (u - b, h)], z0, z1)


def _silindir_x(x0, x1, y, z, r) -> Part:
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0)


def _guney_eksen():
    return p.GAP + p.MENTESE_R, EZ


def _oluk_profili(z_ust: float) -> Part:
    """Güney kenar panel oluğu (tapa ve çerçeve ekinin kesilecek kısmı)."""
    return Pos(_C, 0, 0) * yuva(-_C, _C, ALT - 0.01, ALT + p.DIL_V + p.FIT)


@cache
def cerceve_hucre() -> Part:
    g = p.GAP
    t = _k(g, p.P_XY - g, g, p.P_XY - g, ALT, CUST)
    t -= _k(p.K, p.P_XY - p.K, p.K, p.P_XY - p.K, ALT - 1, CUST + 1)
    guney = (_oluk_profili(CUST)
             + Pos(_C, 0, 0) * anahtar_cebi(ALT, ALT + p.DIL_V + p.FIT, x=-p.ANAHTAR_X))
    for u in p.YUVA_U + (p.YUVA_ORTA,):
        guney += _yarim(u, ALT - 0.01, CUST + 0.01, _F)
    t -= _dort(guney)
    for x, y in delik_noktalari():
        t -= Pos(x, y, ALT) * Cylinder(p.GECIS_DELIK / 2, p.T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return t


@cache
def kapak_hucre() -> Part:
    a, b = _E, p.P_XY - _E
    t = _k(a, b, a, b, CUST, KUST)
    t -= _k(a + p.WALL, b - p.WALL, a + p.WALL, b - p.WALL, CUST + p.WALL, KUST + 1)
    x = p.K + p.KARO_RIB_ARALIK
    while x < p.P_XY - p.K - 1e-6:
        t += _k(x - p.RIB / 2, x + p.RIB / 2, a, b, CUST + p.WALL, KUST)
        t += _k(a, b, x - p.RIB / 2, x + p.RIB / 2, CUST + p.WALL, KUST)
        x += p.KARO_RIB_ARALIK
    for hx in RAY_XLER:
        t += ray(hx, a, b)
    # kaldırmalı kulp kanalları: orta (y = 100) ve ön/arka kenar yarım kanalları
    kw = p.KANAL_W / 2 + _F
    t -= _k(a - 1, b + 1, _C - kw, _C + kw, KANAL_TABAN, KUST + 20)
    t -= _k(a - 1, b + 1, a - 1, kw, KANAL_TABAN, KUST + 20)
    t -= _k(a - 1, b + 1, p.P_XY - kw, b + 1, KANAL_TABAN, KUST + 20)
    # yuvalar: kenarlarda yarım, orta çizgide tam (kulp ayakları)
    ey, ez = _guney_eksen()
    w = p.KANAT_W / 2 + _F
    guney = None
    for u in p.YUVA_U:
        parca = (_yarim(u, CUST - 0.01, KUST + 20, _F)
                 + _silindir_x(u - w, u + w, ey, ez, p.MENTESE_R + _F))       # boğum boşluğu
        guney = parca if guney is None else guney + parca
    guney += _silindir_x(-1, p.P_XY + 1, ey, ez, p.MENTESE_PIM_R + _F)        # pim boşluğu
    t -= _dort(guney)
    for u in p.YUVA_U:
        orta = _yarim(0, CUST - 0.01, KUST + 20, _F)
        t -= Pos(u, _C, 0) * (orta + Rot(0, 0, 180) * orta)
    return t


KAPAK_KAM_H = (KANAL_TABAN - CUST) - _F   # kapak kamı kulp kanallarının altında kalır


@cache
def kam(yukseklik: float = KAM_H) -> Part:
    """Papyon kam (ek yeri y = 0, x = 0 merkezli, z = 0 … yukseklik). Çerçevede KAM_H,
    kapakta KAPAK_KAM_H."""
    a, b = p.PAPYON_A / 2, p.PAPYON_B / 2
    return prizma([(-a, 0), (-b, H), (b, H), (a, 0), (b, -H), (-b, -H)], 0, yukseklik)


def _cerceve_dolgu(u: float) -> Part:
    """Çerçeve yuvasının güney (çevre) yarısını dolduran gövde, panel oluğu profili kesik."""
    return _yarim(u, ALT, CUST - _F, 0, y0=p.GAP) - _oluk_profili(CUST)


@cache
def tapa() -> Part:
    """Çevre kenardaki boş çerçeve yuvası dolgusu (güney kenar, x = 0 merkezli)."""
    return Pos(-_C, 0, 0) * _cerceve_dolgu(_C)      # oluk profili kenar boyunca tam kesilsin diye


@cache
def mentese_cerceve() -> Part:
    """Arka kenar çerçeve menteşe eki (x = YUVA_U[0]): dolgu + dikme + boğum."""
    u, w = p.YUVA_U[0], p.KANAT_W / 2
    ey, ez = _guney_eksen()
    govde = Pos(u - _C, 0, 0) * _cerceve_dolgu(_C)
    # boyun: yuvanın dar ucunda, kapak dışındaki bantta (kapak dönerken süpürmez)
    boyun = _k(u - p.PAPYON_A / 2 + 0.5, u + p.PAPYON_A / 2 - 0.5, p.GAP, _E - _F, CUST - _F - 1, CUST + _F + 1)
    dikme = _k(u - w, u + w, p.GAP, _E - _F, CUST + _F, ez)
    bogum = _silindir_x(u - w, u + w, ey, ez, p.MENTESE_R)
    return _kuzey(govde + boyun + dikme + bogum - _silindir_x(u - w - 1, u + w + 1, ey, ez, p.MENTESE_PIM_R + _F))


@cache
def mentese_kapak() -> Part:
    """Arka kenar kapak menteşe eki (x = YUVA_U[1]): kuyruk eksenin önünde + boğum."""
    u, w = p.YUVA_U[1], p.KANAT_W / 2
    ey, ez = _guney_eksen()
    kuyruk = _yarim(u, CUST + _F, KUST - _F, 0, y0=_E)
    bogum = _silindir_x(u - w, u + w, ey, ez, p.MENTESE_R)
    return _kuzey(kuyruk + bogum - _silindir_x(u - w - 1, u + w + 1, ey, ez, p.MENTESE_PIM_R + _F))


@cache
def mandal_eki() -> Part:
    """Ön kenar kapak mandalı (x = YUVA_U[1]): kapak yuvasında gövde, çerçeve yuvasından inen kol,
    çerçevenin altına takılan dudak. Açmak için öne MANDAL_GERI esnetilir."""
    u = p.YUVA_U[1]
    govde = _yarim(u, CUST + _F, KUST - _F, 0, y0=_E)
    kol = _k(u - 4, u + 4, 9.5, 11.5, ALT - 2.6, CUST + _F + 0.01)
    dudak = _k(u - 4, u + 4, 11.5, H + _F + 3.5, ALT - 2.6, ALT - _F)
    return govde + kol + dudak


def mentese_pimi(x0: float, x1: float) -> Part:
    """Arka kenar menteşe pimi (hücre çerçevesinde)."""
    return _silindir_x(x0, x1, EY, EZ, p.MENTESE_PIM_R)


# --- Paralel kollu katlanır kulp ---------------------------------------------------------
# Kulp çerçevesi: ayak yuvası merkezi (0, 0), kulp ekseni x boyunca, z kutu üstünden.
PIVOT_Z = KANAL_TABAN + p.KANAL_D / 2
_PL0 = p.KULP_CUBUK_W / 2 + _F               # yan plakanın iç yüzü
_PL1 = _PL0 + p.KULP_PLAKA_T


def _silindir_y(x, y0, y1, z, r) -> Part:
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, y1 - y0)


@cache
def kulp_ayagi() -> Part:
    """Yuvaya takılan kulp ayağı: papyon gövde + kanalın iki yanında yanak + kısa pimler."""
    govde = _yarim(0, CUST + _F, KANAL_TABAN - _F, 0)
    govde = govde + Rot(0, 0, 180) * govde
    yanak_y0 = p.KANAL_W / 2 + _F + _F
    yanak = _k(-6, 6, yanak_y0, H - _F, KANAL_TABAN - _F - 0.5, KUST - 0.25)
    pim = _silindir_y(0, _PL0 + _F, yanak_y0 + 0.5, PIVOT_Z, p.KULP_PIM_R)
    tek = yanak + pim
    return govde + tek + tek.mirror(Plane.XZ)


@cache
def kulp_kolu() -> Part:
    """Yan kol plakası (katlı konumda, +y tarafı): ayak pimi x = 0, uç pimi x = KOL."""
    L, h = p.KULP_KOL_L, 2.5
    plaka = _k(-h, L + h, _PL0, _PL1, PIVOT_Z - h, PIVOT_Z + h)
    for x in (0, L):
        plaka -= _silindir_y(x, _PL0 - 1, _PL1 + 1, PIVOT_Z, p.KULP_PIM_R + _F)
    return plaka


@cache
def kulp_cubugu(uzunluk: float) -> Part:
    """Tutma çubuğu (katlı konumda): x = 0 … uzunluk; uçlarda kol pimleri."""
    e = 3.0
    z0 = KANAL_TABAN + _F
    cubuk = _k(-e, uzunluk + e, -p.KULP_CUBUK_W / 2, p.KULP_CUBUK_W / 2, z0, z0 + p.KULP_CUBUK_T)
    for x in (0, uzunluk):
        cubuk += _silindir_y(x, -_PL1, _PL1, PIVOT_Z, p.KULP_PIM_R)
    return cubuk


def kulp_ac_donusumu():
    """Bir kolu ayak pimi etrafında dikleştiren dönüşüm (kulp çerçevesinde, ayak (0,0))."""
    return Pos(0, 0, PIVOT_Z) * Rot(0, -90, 0) * Pos(0, 0, -PIVOT_Z)


KULP_GRUPLARI = {(1, 1), (2, 1), (2, 2)}
