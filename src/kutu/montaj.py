"""Parçaları node ızgarasına yerleştirir: kutu(nx, ny, nz)."""
from dataclasses import dataclass

from build123d import Part, Plane, Pos, Rot

from kutu import params as p
from kutu.parts.cekmece import cekmece as cekmece_parcasi, raf
from kutu.parts.karo import karo_taban
from kutu.parts.kiskac import kiskac, kiskac_dugumu
from kutu.parts.kose import kose, kose_dugumu
from kutu.parts.kulp import acik, kulp as kulp_parcasi
from kutu.parts.panel import panel
from kutu.parts.kapak_mandal import acik_mandal as kapak_acik_mandal, mandal as kapak_mandal
from kutu.lib.papyon import papyon
from kutu.parts import evrensel as ev
from kutu.parts.tavan import (MODUL_ARASI, MODUL_KAM_Z0, cerceve, kapak, kulp_boyu, kulp_yeri,
                               mentese_ekseni, tavan_modulleri)
from kutu.parts.yatay_kiskac import yatay_kiskac


@dataclass
class Yerlesim:
    ad: str
    tur: str
    parca: Part
    patlat: tuple[float, float, float]


_BAS_ASAGI = Pos(0, 0, p.P_Z / 2) * Rot(0, 180, 0) * Pos(0, 0, -p.P_Z / 2)   # kat içinde yüz normali etrafında 180°


def _isaret(v: float) -> int:
    return 0 if abs(v) < 1 else (1 if v > 0 else -1)


def kesisim_hacmi(a: Part, b: Part) -> float:
    ba, bb = a.bounding_box(), b.bounding_box()
    if (
        ba.max.X <= bb.min.X or bb.max.X <= ba.min.X
        or ba.max.Y <= bb.min.Y or bb.max.Y <= ba.min.Y
        or ba.max.Z <= bb.min.Z or bb.max.Z <= ba.min.Z
    ):
        return 0.0
    k = a & b
    return float(k.volume) if k is not None else 0.0


def kutu(nx: int, ny: int, nz: int = 1, kulp: bool = False, kulp_acik: bool = False,
         cekmece: bool = False, kapak_mandal_acik: bool = False, tavan: str = "evrensel",
         kapak_gruplari: list[tuple[int, int, int, int]] | None = None,
         mandal_acik: bool = False) -> list[Yerlesim]:
    """tavan: "modul" (1×1 / 2×1 / 1×2 / 2×2 tek parça modüller) ya da "evrensel"
    (tek tip hücreler + yuva ekleri; kapak_gruplari ile gruplanır)."""
    W, D = nx * p.P_XY, ny * p.P_XY
    out: list[Yerlesim] = []

    def ekle(ad: str, tur: str, parca: Part, zb: float) -> None:
        c = parca.bounding_box().center()
        if tur in ("taban", "cerceve", "kapak", "kapak_mandal", "kulp", "papyon_cerceve") or tur in _EV_TURLER:
            yon = (0, 0, _isaret(c.Z - (zb + p.P_Z / 2)))
        elif tur == "cekmece":
            yon = (0, -1, 0)
        elif tur == "raf":
            yon = (0, 0, 0)
        else:
            yon = (_isaret(c.X - W / 2), _isaret(c.Y - D / 2), 0)
        out.append(Yerlesim(ad, tur, parca, yon))

    for i in range(nx):
        for j in range(ny):
            x0, y0 = i * p.P_XY, j * p.P_XY
            ekle(f"taban_{i}{j}", "taban", Pos(x0, y0, 0) * karo_taban(), 0)
    ust = Pos(0, 0, nz * p.P_Z)
    zu = (nz - 1) * p.P_Z
    mandal_parca = kapak_acik_mandal() if kapak_mandal_acik else kapak_mandal()
    if tavan == "evrensel":
        _evrensel_tavan(ekle, nx, ny, nz, kapak_gruplari, mandal_acik, kulp, kulp_acik)
    moduller = tavan_modulleri(nx, ny) if tavan == "modul" else []
    modul_of = {(i, j): m for m, (i0, j0, mx, my) in enumerate(moduller)
                for i in range(i0, i0 + mx) for j in range(j0, j0 + my)}
    for (i, j), m in sorted(modul_of.items()):                       # modüller arası kamlar
        for di, dj in ((1, 0), (0, 1)):
            n = modul_of.get((i + di, j + dj))
            if n is None or n == m:
                continue
            for u in p.YUVA_U:
                if di:
                    yer = Pos((i + 1) * p.P_XY, j * p.P_XY + u, MODUL_KAM_Z0) * Rot(0, 0, 90)
                else:
                    yer = Pos(i * p.P_XY + u, (j + 1) * p.P_XY, MODUL_KAM_Z0)
                ekle(f"papyon_cerceve_{i}{j}_{di}{dj}_{u:g}", "papyon_cerceve",
                     ust * yer * papyon(MODUL_ARASI), zu)
    for m, (i0, j0, mx, my) in enumerate(moduller):   # tavan modülleri
        o = ust * Pos(i0 * p.P_XY, j0 * p.P_XY, 0)
        ekle(f"m{m}_cerceve_{mx}x{my}", "cerceve", o * cerceve(mx, my), zu)
        ekle(f"m{m}_kapak_{mx}x{my}", "kapak", o * kapak(mx, my), zu)
        for i in range(mx):
            ekle(f"m{m}_kapak_mandal_{i}", "kapak_mandal", o * Pos(i * p.P_XY, 0, 0) * mandal_parca, zu)
        if kulp:
            xs, yc = kulp_yeri(mx, my)
            parca = kulp_parcasi(kulp_boyu(mx))
            if kulp_acik:
                parca = acik(parca)
            ekle(f"m{m}_kulp_{kulp_boyu(mx)}x", "kulp", o * Pos(xs, yc, -p.GAP) * parca, zu)

    for kat in range(nz):
        zb = kat * p.P_Z
        ara = kat < nz - 1   # bu katın üstünde başka kat var: kat arası bant

        for ad, yer in (
            ("gb", Pos(0, 0, zb)),
            ("gd", Pos(W, 0, zb) * Rot(0, 0, 90)),
            ("kd", Pos(W, D, zb) * Rot(0, 0, 180)),
            ("kb", Pos(0, D, zb) * Rot(0, 0, -90)),
        ):
            ekle(f"k{kat}_kose_{ad}", "kose", yer * kose(), zb)
            if ara:
                ekle(f"k{kat}_kose_dugumu_{ad}", "kose_dugumu", yer * kose_dugumu(), zb)

        def duvar(tur: str, parca: Part, x_listesi, y_listesi, on: bool = True, cevir: bool = False) -> None:
            """cevir: batı ve kuzey yüzlerinde parça baş aşağı (yatay yan ray yön kuralı)."""
            ters = _BAS_ASAGI * parca if cevir else parca
            for x in x_listesi:
                if on:
                    ekle(f"k{kat}_{tur}_g{x:g}", tur, Pos(x, 0, zb) * parca, zb)
                ekle(f"k{kat}_{tur}_k{x:g}", tur, Pos(x, D, zb) * Rot(0, 0, 180) * ters, zb)
            for y in y_listesi:
                ekle(f"k{kat}_{tur}_b{y:g}", tur, Pos(0, y, zb) * Rot(0, 0, -90) * ters, zb)
                ekle(f"k{kat}_{tur}_d{y:g}", tur, Pos(W, y, zb) * Rot(0, 0, 90) * parca, zb)

        orta = p.P_XY / 2
        duvar("panel", panel(),
              [orta + i * p.P_XY for i in range(nx)],
              [orta + j * p.P_XY for j in range(ny)], on=not cekmece, cevir=True)
        if cekmece:
            alt = zb + p.T + (p.WALL if kat > 0 else 0)        # taban ya da raf üstü
            ust_plaka = zb + p.T + p.H - p.FIT
            ust_tepsi = ust_plaka if ara else (nz * p.P_Z - p.TEKNE_ALT - p.FIT)
            parca = cekmece_parcasi(zb + p.T + p.FIT, ust_plaka, alt + p.FIT, ust_tepsi)
            for i in range(nx):
                ekle(f"k{kat}_cekmece_{i}", "cekmece", Pos(i * p.P_XY, 0, 0) * parca, zb)
            if ara:
                ekle(f"k{kat}_raf", "raf", raf(nx, ny, kat), zb)
        duvar("kiskac", kiskac(),
              [i * p.P_XY for i in range(1, nx)],
              [j * p.P_XY for j in range(1, ny)])
        if ara:
            duvar("yatay_kiskac", yatay_kiskac(),
                  [orta + i * p.P_XY for i in range(nx)],
                  [orta + j * p.P_XY for j in range(ny)])
            duvar("kiskac_dugumu", kiskac_dugumu(),
                  [i * p.P_XY for i in range(1, nx)],
                  [j * p.P_XY for j in range(1, ny)])
    return out


_EV_TURLER = ("cerceve_hucre", "kapak_hucre", "kam_cerceve", "kam_kapak", "tapa",
              "mentese_cerceve", "mentese_kapak", "mentese_pimi", "mandal_eki",
              "kulp_ayagi", "kulp_kolu", "kulp_cubugu")


def _kenar_yeri(i: int, j: int, kenar: str):
    """Hücre (i, j)'nin kenarı için güney→kenar dönüşümü (hücre merkezi etrafında)."""
    c = p.P_XY / 2
    aci = {"g": 0, "d": 90, "k": 180, "b": 270}[kenar]
    return Pos(i * p.P_XY + c, j * p.P_XY + c, 0) * Rot(0, 0, aci) * Pos(-c, -c, 0)


def _evrensel_tavan(ekle, nx: int, ny: int, nz: int, gruplar, mandal_acik: bool,
                    kulp: bool = False, kulp_acik: bool = False) -> None:
    """Evrensel tavan: tek tip çerçeve/kapak hücreleri + kamlar, tapalar, menteşe ve mandal ekleri."""
    P = p.P_XY
    ust = Pos(0, 0, nz * p.P_Z)
    zu = (nz - 1) * p.P_Z
    gruplar = gruplar or [(0, 0, nx, ny)]
    grup_of = {}
    for g, (i0, j0, gx, gy) in enumerate(gruplar):
        for i in range(i0, i0 + gx):
            for j in range(j0, j0 + gy):
                grup_of[(i, j)] = g
    assert len(grup_of) == nx * ny, "kapak grupları tavanı tam ve örtüşmeden kaplamalı"
    u_men_cer, u_men_kap, u_man = P - p.YUVA_U[0], P - p.YUVA_U[1], p.YUVA_U[1]   # x konumları
    arka = {(i, j0 + gy - 1) for (i0, j0, gx, gy) in gruplar for i in range(i0, i0 + gx)}
    # kulp ayaklarının oturduğu ek yeri yuvaları (2×2 gruplar): kapak kamı yok
    ayak_ek = set()
    if kulp:
        for grup in gruplar:
            ki0, kj0, kx, ky = kulp_blogu(*grup)
            if ky == 2:
                ayak_ek |= {(ki0, kj0, p.YUVA_U[0]), (ki0 + kx - 1, kj0, p.YUVA_U[1])}
    on = {(i, j0) for (i0, j0, gx, gy) in gruplar for i in range(i0, i0 + gx)}

    for i in range(nx):
        for j in range(ny):
            g = grup_of[(i, j)]
            o = ust * Pos(i * P, j * P, 0)
            ekle(f"cerceve_hucre_{i}{j}", "cerceve_hucre", o * ev.cerceve_hucre(), zu)
            ekle(f"g{g}_kapak_hucre_{i}{j}", "kapak_hucre", o * ev.kapak_hucre(), zu)
            # iç ek yerleri (doğu ve kuzey komşusu)
            for di, dj in ((1, 0), (0, 1)):
                ni, nj = i + di, j + dj
                if ni >= nx or nj >= ny:
                    continue
                for u in p.YUVA_U + (p.YUVA_ORTA,):
                    yer = (Pos((i + 1) * P, j * P + u, 0) * Rot(0, 0, 90) if di
                           else Pos(i * P + u, (j + 1) * P, 0))
                    # grup sınırında menteşe/mandal yuvaları dolu
                    if dj and (i, j) in arka and (i, nj) in on and grup_of[(i, nj)] != g and u == u_man:
                        continue
                    ekle(f"kam_cerceve_{i}{j}_{di}{dj}_{u:g}", "kam_cerceve",
                         ust * yer * Pos(0, 0, ev.ALT) * ev.kam(), zu)
                    if u != p.YUVA_ORTA and grup_of[(ni, nj)] == g and not (dj and (i, j, u) in ayak_ek):
                        ekle(f"g{g}_kam_kapak_{i}{j}_{di}{dj}_{u:g}", "kam_kapak",
                             ust * yer * Pos(0, 0, ev.CUST) * ev.kam(ev.KAPAK_KAM_H), zu)
            # çevre kenarlarda tapalar (menteşe ve mandal konumları hariç)
            for kenar, cevre in (("g", j == 0), ("k", j == ny - 1), ("b", i == 0), ("d", i == nx - 1)):
                if not cevre:
                    continue
                for u in p.YUVA_U + (p.YUVA_ORTA,):
                    if kenar == "k" and (i, j) in arka and u == p.YUVA_U[0]:
                        continue          # çerçeve menteşe eki (kuzey kenarda x = P − YUVA_U[0])
                    if kenar == "g" and (i, j) in on and u == u_man:
                        continue          # mandal eki
                    ekle(f"tapa_{i}{j}_{kenar}_{u:g}", "tapa",
                         ust * _kenar_yeri(i, j, kenar) * Pos(u, 0, 0) * ev.tapa(), zu)

    for g, (i0, j0, gx, gy) in enumerate(gruplar):
        jb = j0 + gy - 1
        for i in range(i0, i0 + gx):
            o = ust * Pos(i * P, jb * P, 0)
            ekle(f"mentese_cerceve_{g}_{i}", "mentese_cerceve", o * ev.mentese_cerceve(), zu)
            ekle(f"g{g}_mentese_kapak_{i}", "mentese_kapak", o * ev.mentese_kapak(), zu)
            m = ev.mandal_eki()
            if mandal_acik:
                m = Pos(0, -p.MANDAL_GERI, 0) * m
            ekle(f"g{g}_mandal_eki_{i}", "mandal_eki", ust * Pos(i * P, j0 * P, 0) * m, zu)
        if kulp:
            _evrensel_kulp(ekle, g, *kulp_blogu(i0, j0, gx, gy), ust, zu, kulp_acik)
        x0 = i0 * P + min(u_men_cer, u_men_kap) - p.KANAT_W / 2
        x1 = (i0 + gx - 1) * P + max(u_men_cer, u_men_kap) + p.KANAT_W / 2
        ekle(f"mentese_pimi_{g}", "mentese_pimi", ust * Pos(0, jb * P, 0) * ev.mentese_pimi(x0, x1), zu)


def kulp_blogu(i0: int, j0: int, gx: int, gy: int) -> tuple[int, int, int, int]:
    """Grubun kulbu: grubun ortasındaki node'lar (tek sayıda node: 1, çift: 2; x ve y'de ayrı)."""
    kx, ky = 1 if gx % 2 else 2, 1 if gy % 2 else 2
    return i0 + (gx - kx) // 2, j0 + (gy - ky) // 2, kx, ky


def _evrensel_kulp(ekle, g, i0, j0, gx, gy, ust, zu, acik: bool) -> None:
    """Paralel kollu katlanır kulp: ayaklar grup kenarlarından KULP_AYAK_U içeride, grup ortası hizasında."""
    P = p.P_XY
    yc = (j0 + gy / 2) * P
    xa, xb = i0 * P + p.KULP_AYAK_U, (i0 + gx) * P - p.KULP_AYAK_U
    L = p.KULP_KOL_L
    kol_don = ev.kulp_ac_donusumu() if acik else Pos(0, 0, 0)
    for n, xf in enumerate((xa, xb)):
        f = ust * Pos(xf, yc, 0)
        ekle(f"g{g}_kulp_ayagi_{n}", "kulp_ayagi", f * ev.kulp_ayagi(), zu)
        kol = kol_don * ev.kulp_kolu()
        ekle(f"g{g}_kulp_kolu_{n}a", "kulp_kolu", f * kol, zu)
        ekle(f"g{g}_kulp_kolu_{n}b", "kulp_kolu", f * kol_don * ev.kulp_kolu_ayna(), zu)
    cubuk = ev.kulp_cubugu(xb - xa)
    yer = Pos(xa, yc, ev.PIVOT_Z + L) * Pos(0, 0, -ev.PIVOT_Z) if acik else Pos(xa + L, yc, 0)
    ekle(f"g{g}_kulp_cubugu", "kulp_cubugu", ust * yer * cubuk, zu)


def evrensel_grup_ac(liste: list[Yerlesim], g: int, aci: float, nx: int, ny: int, nz: int,
                     gruplar=None) -> list[Yerlesim]:
    """Evrensel tavanda g. kapak grubunu (g{g}_ önekli parçalar) kendi menteşesi etrafında açar."""
    gruplar = gruplar or [(0, 0, nx, ny)]
    _, j0, _, gy = gruplar[g]
    y = (j0 + gy - 1) * p.P_XY + ev.EY
    z = nz * p.P_Z + ev.EZ
    don = Pos(0, y, z) * Rot(-aci, 0, 0) * Pos(0, -y, -z)
    return [Yerlesim(e.ad, e.tur, don * e.parca, e.patlat) for e in liste if e.ad.startswith(f"g{g}_")]


def kapak_ac(liste: list[Yerlesim], my: int, nz: int, aci: float, y0: float = 0.0) -> list[Yerlesim]:
    """Bir tavan modülünün kapak grubunu (kapak, mandallar, kulp) menteşe ekseni etrafında açar.

    my: modülün derinliği (node), y0: modülün kutu içindeki y başlangıcı.
    """
    ya, za = mentese_ekseni(my)
    y, z = y0 + ya, nz * p.P_Z + za
    don = Pos(0, y, z) * Rot(-aci, 0, 0) * Pos(0, -y, -z)
    return [Yerlesim(e.ad, e.tur, don * e.parca, e.patlat) for e in liste]
