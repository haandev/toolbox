"""STEP (kalıpçı), STL (prototip) ve önizleme (konumlu STL + manifest) çıktıları."""
import argparse
import json
from pathlib import Path

from build123d import Pos, Rot, export_step, export_stl

from kutu import params as p
from kutu.kalip import egimsiz_yuz_sayisi
from kutu.lib.kilit_yeri import kilit_noktalari
from kutu.baski import kulp_baski_parcalari, modul_baski_parcalari
from kutu.montaj import evrensel_grup_ac, kapak_ac, kutu
from kutu.parts import evrensel as ev
from kutu.parts.karo import karo_taban
from kutu.parts.kiskac import kiskac, kiskac_dugumu
from kutu.parts.kose import kose, kose_dugumu
from kutu.parts.kulp import kulp
from kutu.parts.cekmece import cekmece, raf
from kutu.parts.panel import panel
from kutu.parts.kapak_mandal import mandal as kapak_mandal
from kutu.parts.tavan import cerceve, kapak
from kutu.parts.yatay_kiskac import yatay_kiskac

TURLER = {"panel": panel, "kose": kose, "kiskac": kiskac, "taban": karo_taban,
          "cerceve": lambda: cerceve(1, 1), "kapak": lambda: kapak(1, 1), "kapak_mandal": kapak_mandal,
          "cerceve_2x1": lambda: cerceve(2, 1), "kapak_2x1": lambda: kapak(2, 1),
          "cerceve_2x2": lambda: cerceve(2, 2), "kapak_2x2": lambda: kapak(2, 2),
                    "cekmece": lambda: cekmece(p.T + p.FIT, p.T + p.H - p.FIT, p.T + p.FIT, p.P_Z - p.TEKNE_ALT - p.FIT),
          "raf_1x1": lambda: raf(1, 1, 0), "kulp_1x": lambda: kulp(1), "kulp_2x": lambda: kulp(2),
          "yatay_kiskac": yatay_kiskac, "kose_dugumu": kose_dugumu, "kiskac_dugumu": kiskac_dugumu}
_Z = (0, 0, 1)
CEKME = {"panel": (0, 1, 0), "yatay_kiskac": (0, 1, 0)}   # diğerleri Z
RENKLER = {"taban": "#5b6270", "cerceve": "#4a5060", "kapak": "#8a94a6", "kapak_mandal": "#8e44ad", "kose": "#f39c3d", "kiskac": "#f1c40f",
           "panel": "#9fb3c8", "yatay_kiskac": "#2ecc9a", "kose_dugumu": "#d35400",
           "kiskac_dugumu": "#b7950b", "kulp": "#e74c3c", "papyon_kapak": "#e67e22",
           "kulp_ucu": "#e74c3c", "kulp_cubugu": "#bdc3c7",
           "cerceve_hucre": "#4a5060", "kapak_hucre": "#8a94a6", "kam_cerceve": "#e67e22",
           "kam_kapak": "#e67e22", "tapa": "#2c3e50", "mentese_cerceve": "#16a085",
           "mentese_kapak": "#1abc9c", "mentese_pimi": "#7f8c8d", "mandal_eki": "#8e44ad",
           "kulp_ayagi": "#c0392b", "kulp_kolu": "#e74c3c",
           "cekmece": "#5dade2", "raf": "#95a5a6"}


def disa_aktar(cikti: Path, nx: int, ny: int, nz: int) -> dict:
    for alt in ("step", "stl", "preview"):
        (cikti / alt).mkdir(parents=True, exist_ok=True)

    for tur, fn in TURLER.items():
        parca = fn()
        export_step(parca, str(cikti / "step" / f"{tur}.step"))
        export_stl(parca, str(cikti / "stl" / f"{tur}.stl"))
        print(f"{tur:7s} eğimsiz yüz: {egimsiz_yuz_sayisi(parca, CEKME.get(tur, _Z))}")

    onizleme = cikti / "preview"
    for eski in onizleme.glob("*.stl"):
        eski.unlink()
    parcalar = []
    for y in kutu(nx, ny, nz, kulp=True):
        dosya = f"{y.ad}.stl"
        export_stl(y.parca, str(onizleme / dosya))
        parcalar.append({"ad": y.ad, "tur": y.tur, "dosya": dosya,
                         "renk": RENKLER[y.tur], "patlat": list(y.patlat)})

    manifest = {
        "kutu": {"nx": nx, "ny": ny, "nz": nz, "P_XY": int(p.P_XY), "P_Z": int(p.P_Z)},
        "parcalar": parcalar,
        "kilit": [{"yuz": yuz, "merkez": list(m)} for yuz, m in kilit_noktalari(nx, ny, nz)],
    }
    (onizleme / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    return manifest


def sahne_aktar(cikti: Path, ad: str, gruplar, sinir: tuple[float, float, float]) -> dict:
    """Birden çok kutuyu tek önizleme sahnesine yazar (out/<ad>, ?m=<ad>).

    gruplar: (ön ek, yerleşim listesi, Location, patlatma z eki) dörtlüleri.
    """
    klasor = cikti / ad
    klasor.mkdir(parents=True, exist_ok=True)
    for eski in klasor.glob("*.stl"):
        eski.unlink()
    parcalar = []
    for on_ek, liste, yer, z_ek in gruplar:
        for y in liste:
            dosya = f"{on_ek}_{y.ad}.stl"
            export_stl(yer * y.parca, str(klasor / dosya))
            parcalar.append({"ad": f"{on_ek}_{y.ad}", "tur": y.tur, "dosya": dosya, "renk": RENKLER[y.tur],
                             "patlat": [y.patlat[0], y.patlat[1], y.patlat[2] + z_ek]})
    manifest = {"sahne": {"x0": 0, "x1": sinir[0], "y0": 0, "y1": sinir[1], "z0": 0, "z1": sinir[2]},
                "parcalar": parcalar, "kilit": []}
    (klasor / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    return manifest


def istif_aktar(cikti: Path) -> dict:
    """40×20 kutunun üstünde 200 mm kaydırılmış 20×20 kutu: erkek–dişi istif önizlemesi."""
    return sahne_aktar(cikti, "istif", [
        ("alt", kutu(2, 1, 1, kulp=True), Pos(0, 0, 0), 0),
        ("ust", kutu(1, 1, 1, kulp=True), Pos(p.P_XY, 0, p.P_Z), 2),
    ], (2 * p.P_XY, p.P_XY, 2 * p.P_Z))


def yan_yana_aktar(cikti: Path) -> dict:
    """Yan kilit: 20×20 kutunun yanında 180° döndürülmüş 20×20 ve onun yanında 2H kutu."""
    c = p.P_XY / 2
    donuk = Pos(p.P_XY, 0, 0) * Pos(c, c, 0) * Rot(0, 0, 180) * Pos(-c, -c, 0)
    return sahne_aktar(cikti, "yan", [
        ("a", kutu(1, 1, 1), Pos(0, 0, 0), 0),
        ("b", kutu(1, 1, 1), donuk, 0),
        ("c", kutu(1, 1, 2), Pos(2 * p.P_XY, 0, 0), 0),
    ], (3 * p.P_XY, p.P_XY, 2 * p.P_Z))


def kulp_sahnesi_aktar(cikti: Path) -> dict:
    """Evrensel tavanda kulp grupları: 1×1, 2×1, 2×2 (açık) ve 3×2 kutu: 2×2 + iki 1×1 grup."""
    return sahne_aktar(cikti, "kulp", [
        ("a", kutu(1, 1, 1, kulp=True, kulp_acik=True), Pos(0, 0, 0), 0),
        ("b", kutu(2, 1, 1, kulp=True, kulp_acik=True), Pos(300, 0, 0), 0),
        ("c", kutu(2, 2, 1, kulp=True, kulp_acik=True), Pos(0, 300, 0), 0),
        ("d", kutu(3, 2, 1, kulp=True, kulp_acik=True,
                   kapak_gruplari=[(0, 0, 2, 2), (2, 0, 1, 1), (2, 1, 1, 1)]), Pos(500, 300, 0), 0),
    ], (1100, 700, 2 * p.P_Z))


def cekmece_sahnesi_aktar(cikti: Path) -> dict:
    """Çekmeceli kutular: 1×1 (çekmece yarı açık), 2×1×2 (alt sol açık), istifli."""
    def ac(liste, adlar, dy):
        return [type(y)(y.ad, y.tur, Pos(0, -dy, 0) * y.parca, y.patlat) if y.ad in adlar else y for y in liste]
    a = ac(kutu(1, 1, 1, kulp=True, cekmece=True), {"k0_cekmece_0"}, 100)
    b = ac(kutu(2, 1, 2, kulp=True, cekmece=True), {"k0_cekmece_0", "k1_cekmece_1"}, 120)
    return sahne_aktar(cikti, "cekmece", [
        ("a", a, Pos(0, 0, 0), 0),
        ("b", b, Pos(300, 0, 0), 0),
    ], (700, p.P_XY, 2 * p.P_Z))


def duvar_sahnesi_aktar(cikti: Path) -> dict:
    """Kayar duvar: 3 sütun × 2 kat 1×1 kutu; alt orta kutu öne çekilmiş, üstündeki komşu raylarında asılı."""
    gruplar = []
    for i in range(3):
        for k in range(2):
            dy = -110 if (i, k) == (1, 0) else 0
            gruplar.append((f"{i}{k}", kutu(1, 1, 1, kulp=True), Pos(i * p.P_XY, dy, k * p.P_Z), 0))
    return sahne_aktar(cikti, "duvar", gruplar, (3 * p.P_XY, p.P_XY, 2 * p.P_Z))


def karma_gruplar():
    """Karma istif: farklı boyutlar, kutusu çekmece gibi çekilmiş kutu, iç çekmeceli kutu.

    (ön ek, yerleşim listesi, Location) üçlüleri.
    """
    P, Z = p.P_XY, p.P_Z

    def ac(liste, ad, dy):
        return [type(y)(y.ad, y.tur, Pos(0, dy, 0) * y.parca, y.patlat) if y.ad == ad else y for y in liste]

    return [
        ("A_2x1", kutu(2, 1, 1, kulp=True), Pos(0, 0, 0)),
        ("B_cekmeceli", ac(kutu(1, 1, 1, kulp=True, cekmece=True), "k0_cekmece_0", -90), Pos(2 * P, 0, 0)),
        ("C", kutu(1, 1, 1, kulp=True), Pos(0, 0, Z)),
        ("D_cekilmis", kutu(1, 1, 1, kulp=True), Pos(P, -110, Z)),
        ("E", kutu(1, 1, 1, kulp=True), Pos(2 * P, 0, Z)),
        ("F_3x1", kutu(3, 1, 1, kulp=True, kapak_gruplari=[(0, 0, 2, 1), (2, 0, 1, 1)]), Pos(0, 0, 2 * Z)),
        ("G_2h", kutu(1, 1, 2, kulp=True), Pos(3 * P, 0, 0)),
    ]


def karma_sahnesi_aktar(cikti: Path) -> dict:
    return sahne_aktar(cikti, "karma", [(a, l, yer, 0) for a, l, yer in karma_gruplar()],
                       (4 * p.P_XY, p.P_XY, 3 * p.P_Z))


def kapak_sahnesi_aktar(cikti: Path) -> dict:
    """Evrensel tavan: 1×1 (90° açık), 2×1 (60°), 2×2 iki satır grup (arka grup 90° açık)."""
    def acik(nx, ny, gruplar, acilacak):
        k = kutu(nx, ny, 1, kulp=True, kapak_gruplari=gruplar, mandal_acik=True)
        out = list(k)
        for g, aci in acilacak:
            grup = evrensel_grup_ac(k, g, aci, nx, ny, 1, gruplar)
            adlar = {y.ad for y in grup}
            out = [y for y in out if y.ad not in adlar] + grup
        return out
    iki = [(0, 0, 2, 1), (0, 1, 2, 1)]
    return sahne_aktar(cikti, "kapak", [
        ("a", acik(1, 1, None, [(0, 90)]), Pos(0, 0, 0), 0),
        ("b", acik(2, 1, None, [(0, 60)]), Pos(300, 0, 0), 0),
        ("c", acik(2, 2, iki, [(1, 90)]), Pos(800, 0, 0), 0),
    ], (1200, 2 * p.P_XY, 2 * p.P_Z))


def baski_aktar(cikti: Path) -> list[Path]:
    """Baskı STL'leri: her tavan modülünün node parçaları ve kamları, 2× kulp parçaları (out/baski)."""
    klasor = cikti / "baski"
    klasor.mkdir(parents=True, exist_ok=True)
    dosyalar = []
    for mx, my in ((1, 1), (2, 1), (1, 2), (2, 2)):
        for ad, _, parca in modul_baski_parcalari(mx, my):
            d = klasor / f"tavan_{mx}x{my}_{ad}.stl"
            export_stl(parca, str(d))
            dosyalar.append(d)
    for ad, _, parca in kulp_baski_parcalari(2):
        d = klasor / f"kulp_2x_{ad}.stl"
        export_stl(parca, str(d))
        dosyalar.append(d)
    evrensel = {"cerceve_hucre": ev.cerceve_hucre(), "kapak_hucre": ev.kapak_hucre(),
                "kam_cerceve": ev.kam(), "kam_kapak": ev.kam(ev.KAPAK_KAM_H), "tapa": ev.tapa(),
                "mentese_cerceve": ev.mentese_cerceve(), "mentese_kapak": ev.mentese_kapak(),
                "mandal_eki": ev.mandal_eki(), "kulp_ayagi": ev.kulp_ayagi(), "kulp_kolu": ev.kulp_kolu()}
    for ad, parca in evrensel.items():
        d = klasor / f"evrensel_{ad}.stl"
        export_stl(parca, str(d))
        dosyalar.append(d)
    return dosyalar


def baski_sahnesi_aktar(cikti: Path) -> dict:
    """2×2 tavan modülünün baskı parçaları açılmış hâlde (patlatma ile)."""
    from kutu.montaj import Yerlesim
    liste = []
    for ad, tur, parca in modul_baski_parcalari(2, 2):
        c = parca.bounding_box().center()
        yon = (1 if c.X > p.P_XY else -1, 1 if c.Y > p.P_XY else -1, 1 if tur == "papyon_kapak" else 0)
        if tur == "cerceve":
            yon = (yon[0], yon[1], -1)
        liste.append(Yerlesim(ad, tur, parca, yon))
    for ad, tur, parca in kulp_baski_parcalari(2):
        liste.append(Yerlesim(ad, tur, Pos(0, p.P_XY, -p.GAP) * parca, (0, 0, 2)))
    return sahne_aktar(cikti, "baski_onizleme", [("m", liste, Pos(0, 0, 0), 0)], (2 * p.P_XY, 2 * p.P_XY, 40))


def main() -> None:
    ap = argparse.ArgumentParser(description="Modüler kutu çıktıları")
    ap.add_argument("--nx", type=int, default=1)
    ap.add_argument("--ny", type=int, default=1)
    ap.add_argument("--nz", type=int, default=1)
    ap.add_argument("--cikti", type=Path, default=Path("out"))
    ap.add_argument("--istif", action="store_true", help="istif önizlemesi (out/istif)")
    ap.add_argument("--yan", action="store_true", help="yan kilit önizlemesi (out/yan)")
    ap.add_argument("--kulp", action="store_true", help="kulp önizlemesi (out/kulp)")
    ap.add_argument("--cekmece", action="store_true", help="çekmece önizlemesi (out/cekmece)")
    ap.add_argument("--duvar", action="store_true", help="kayar duvar önizlemesi (out/duvar)")
    ap.add_argument("--karma", action="store_true", help="karma istif önizlemesi (out/karma)")
    ap.add_argument("--kapak", action="store_true", help="açık kapak önizlemesi (out/kapak)")
    ap.add_argument("--baski", action="store_true", help="baskı STL'leri (out/baski) + önizleme (?m=baski_onizleme)")
    a = ap.parse_args()
    if a.baski:
        print(len(baski_aktar(a.cikti)), "STL → out/baski/")
        print(len(baski_sahnesi_aktar(a.cikti)["parcalar"]), "parça → out/baski_onizleme/manifest.json")
        return
    if a.kapak:
        print(len(kapak_sahnesi_aktar(a.cikti)["parcalar"]), "parça → out/kapak/manifest.json")
        return
    if a.karma:
        print(len(karma_sahnesi_aktar(a.cikti)["parcalar"]), "parça → out/karma/manifest.json")
        return
    if a.duvar:
        print(len(duvar_sahnesi_aktar(a.cikti)["parcalar"]), "parça → out/duvar/manifest.json")
        return
    if a.cekmece:
        print(len(cekmece_sahnesi_aktar(a.cikti)["parcalar"]), "parça → out/cekmece/manifest.json")
        return
    if a.kulp:
        print(len(kulp_sahnesi_aktar(a.cikti)["parcalar"]), "parça → out/kulp/manifest.json")
        return
    if a.istif or a.yan:
        if a.istif:
            print(len(istif_aktar(a.cikti)["parcalar"]), "parça → out/istif/manifest.json")
        if a.yan:
            print(len(yan_yana_aktar(a.cikti)["parcalar"]), "parça → out/yan/manifest.json")
        return
    m = disa_aktar(a.cikti, a.nx, a.ny, a.nz)
    print(f"{len(m['parcalar'])} parça → {a.cikti}/preview/manifest.json")


if __name__ == "__main__":
    main()
