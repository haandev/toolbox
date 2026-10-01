"""3D baskı için bölme: tavan modülleri node boyunda parçalara, 2× kulp uçlar + çubuğa.

Kalıp üretiminde modül ve kulp tek parçadır (`cerceve`, `kapak`, `kulp`). Baskıda:
- Çerçeve ve kapak, modülün iç node çizgilerinden (x, y = P_XY·k) KESIM boşlukla bölünür.
  Modül içinde çerçeve kenarı yoktur; kulp parçaların üstünden kesintisiz geçer.
- Kapak parçaları kesim boyunca alttan takılan papyon kamlarla birleşir (yuva büyük ölçüde
  dolu malzemeye denk gelen konumlarda; kulp kanalı ve tekne atlanır).
- Çerçeve parçaları kesimde kamsızdır (kesimler node köşelerindeki vida deliklerine denk
  gelir): çevrede kıskaç vidaları, içeride modüller arası kamlar tutar.
- 2× kulp: iki kulp ucu (kol + mafsal pimi + çubuk yuvası) ve standart çubuk.
"""
from build123d import Box, Cylinder, Part, Plane, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.papyon import papyon, yarim_yuva
from kutu.parts.kulp import EKSEN_Y, KULP_Z0, KULP_Z1, MAFSAL_Z, TUTMA_Y, kulp_x0
from kutu.parts.tavan import _KAPAK_ALT, cerceve, kapak

TABLA = 256.0                 # yaygın baskı tablası (mm)
KESIM = 2 * p.FIT             # parçalar arası kesim boşluğu
_ADAY_U = ((30.0, 170.0), (12.0, 188.0))   # kam aday konumları (node kenarı boyunca); ikincisi yedek
_DOLULUK = 0.6                # yuvanın en az bu oranı malzemeye denk gelmeli


def _k(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)


def _tam_yuva(z0: float, z1: float) -> Part:
    """Kesim çizgisi y = 0'da, iki tarafa açılan tam papyon yuvası (x = 0 merkezli)."""
    yarim = yarim_yuva(0, KESIM, z0, z1)
    return yarim + Rot(0, 0, 180) * yarim


def _kesimler(mx: int, my: int):
    """(Location, eksen) — kesim çizgileri üzerindeki aday kam konumları, node kenarı başına gruplu."""
    for k in range(1, mx):                  # dikey kesim x = k·P, kam x boyunca
        for j in range(my):
            yield [Pos(k * p.P_XY, j * p.P_XY + u, 0) * Rot(0, 0, 90) for u in _ADAY_U[0]], \
                  [Pos(k * p.P_XY, j * p.P_XY + u, 0) * Rot(0, 0, 90) for u in _ADAY_U[1]]
    for k in range(1, my):                  # yatay kesim y = k·P, kam y boyunca
        for i in range(mx):
            yield [Pos(i * p.P_XY + u, k * p.P_XY, 0) for u in _ADAY_U[0]], \
                  [Pos(i * p.P_XY + u, k * p.P_XY, 0) for u in _ADAY_U[1]]


def _bolge(i: int, j: int, mx: int, my: int) -> Part:
    h = KESIM / 2
    x0 = i * p.P_XY + (h if i > 0 else -5)
    x1 = (i + 1) * p.P_XY - (h if i < mx - 1 else -5)
    y0 = j * p.P_XY + (h if j > 0 else -5)
    y1 = (j + 1) * p.P_XY - (h if j < my - 1 else -5)
    return _k(x0, x1, y0, y1, -100, 100)


def modul_baski_parcalari(mx: int, my: int) -> list[tuple[str, str, Part]]:
    """[(ad, tür, parça)] — tür: 'cerceve', 'kapak', 'papyon_kapak'; montaj konumunda."""
    z0, z1 = _KAPAK_ALT - 0.01, _KAPAK_ALT + p.PAPYON_H + p.FIT
    kp = kapak(mx, my)
    kamlar = []
    yuva_tum = None
    for asil, yedek in _kesimler(mx, my):
        secilen = []
        for adaylar in (asil, yedek):
            for yer in adaylar:
                yuva = yer * _tam_yuva(z0, z1)
                dolu = (kp & yuva)
                if dolu is not None and dolu.volume >= _DOLULUK * yuva.volume:
                    secilen.append(yer)
            if secilen:
                break
        for yer in secilen:
            yuva = yer * _tam_yuva(z0, z1)
            yuva_tum = yuva if yuva_tum is None else yuva_tum + yuva
            kamlar.append(yer * Pos(0, 0, _KAPAK_ALT) * papyon(KESIM))
    if yuva_tum is not None:
        kp = kp - yuva_tum

    out = []
    cr = cerceve(mx, my)
    for tur, ana in (("cerceve", cr), ("kapak", kp)):
        n = 0
        for j in range(my):
            for i in range(mx):
                parca = ana & _bolge(i, j, mx, my)
                if parca is not None and parca.volume > 1:
                    out.append((f"{tur}_{n}", tur, parca))
                    n += 1
    out += [(f"papyon_kapak_{n}", "papyon_kapak", k) for n, k in enumerate(kamlar)]
    return out


def kulp_baski_parcalari(n: int) -> list[tuple[str, str, Part]]:
    """2× (ya da daha uzun) kulp: iki kulp ucu + çubuk. Kulp çerçevesinde (bkz. parts/kulp.py)."""
    x0 = kulp_x0()
    x1 = n * p.P_XY - x0
    h = KULP_Z1 - KULP_Z0
    zc = (KULP_Z0 + KULP_Z1) / 2
    r_cubuk, r_yuva, gobek_l, yuva_d = h / 2 - 2, h / 2 - 2 + p.FIT, 15.0, 12.0

    def sol_uc() -> Part:
        kol_y0 = EKSEN_Y - p.MAFSAL_W / 2
        kol = _k(x0, x0 + p.KOL_T, kol_y0, TUTMA_Y + p.KULP_W / 2, KULP_Z0, KULP_Z1)
        pim_boy = p.MAFSAL_L - 1
        pim = Pos(x0 - pim_boy / 2, EKSEN_Y, MAFSAL_Z) * Rot(0, 90, 0) * Cylinder(p.PIM_D / 2, pim_boy)
        gobek_x0 = x0 + p.KOL_T
        gobek = Pos(gobek_x0 + gobek_l / 2, TUTMA_Y, zc) * Rot(0, 90, 0) * Cylinder(h / 2, gobek_l)
        yuva = Pos(gobek_x0 + gobek_l - yuva_d / 2, TUTMA_Y, zc) * Rot(0, 90, 0) * Cylinder(r_yuva, yuva_d + 0.02)
        return kol + pim + gobek - yuva

    sol = sol_uc()
    sag = Pos(n * p.P_XY, 0, 0) * sol.mirror(Plane.YZ)
    c0 = x0 + p.KOL_T + gobek_l - yuva_d
    c1 = x1 - p.KOL_T - gobek_l + yuva_d
    cubuk = Pos((c0 + c1) / 2, TUTMA_Y, zc) * Rot(0, 90, 0) * Cylinder(r_cubuk, c1 - c0)
    return [("kulp_ucu_sol", "kulp_ucu", sol), ("kulp_ucu_sag", "kulp_ucu", sag),
            ("kulp_cubugu", "kulp_cubugu", cubuk)]
