"""STEP (kalıpçı), STL (prototip) ve önizleme (konumlu STL + manifest) çıktıları."""
import argparse
import json
from pathlib import Path

from build123d import Pos, Rot, export_step, export_stl

from kutu import params as p
from kutu.kalip import egimsiz_yuz_sayisi
from kutu.lib.kilit_yeri import kilit_noktalari
from kutu.montaj import kutu
from kutu.parts.karo import karo_taban
from kutu.parts.kiskac import kiskac, kiskac_dugumu
from kutu.parts.kose import kose, kose_dugumu
from kutu.parts.kulp import kulp
from kutu.parts.cekmece import cekmece, raf
from kutu.parts.panel import panel
from kutu.parts.tavan import tavan
from kutu.parts.yatay_kiskac import yatay_kiskac

TURLER = {"panel": panel, "kose": kose, "kiskac": kiskac, "taban": karo_taban,
          "tavan": lambda: tavan(1, 1), "tavan_2x1": lambda: tavan(2, 1),
          "tavan_3x1": lambda: tavan(3, 1), "tavan_2x2": lambda: tavan(2, 2),
                    "cekmece": lambda: cekmece(p.T + p.FIT, p.T + p.H - p.FIT, p.T + p.FIT, p.P_Z - p.TEKNE_ALT - p.FIT),
          "raf_1x1": lambda: raf(1, 1, 0), "kulp_1x": lambda: kulp(1), "kulp_2x": lambda: kulp(2), "kulp_3x": lambda: kulp(3),
          "yatay_kiskac": yatay_kiskac, "kose_dugumu": kose_dugumu, "kiskac_dugumu": kiskac_dugumu}
_Z = (0, 0, 1)
CEKME = {"panel": (0, 1, 0), "yatay_kiskac": (0, 1, 0)}   # diğerleri Z
RENKLER = {"taban": "#5b6270", "tavan": "#7a8394", "kose": "#f39c3d", "kiskac": "#f1c40f",
           "panel": "#9fb3c8", "yatay_kiskac": "#2ecc9a", "kose_dugumu": "#d35400",
           "kiskac_dugumu": "#b7950b", "kulp": "#e74c3c",
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
    """1×1 (açık kulp), 2×1 (katlı), 3×1 (açık) ve 2×2 (açık) kutular yan yana."""
    return sahne_aktar(cikti, "kulp", [
        ("a", kutu(1, 1, 1, kulp=True, kulp_acik=True), Pos(0, 0, 0), 0),
        ("b", kutu(2, 1, 1, kulp=True), Pos(0, 300, 0), 0),
        ("c", kutu(3, 1, 1, kulp=True, kulp_acik=True), Pos(0, 600, 0), 0),
        ("d", kutu(2, 2, 1, kulp=True, kulp_acik=True), Pos(700, 0, 0), 0),
    ], (1100, 800, 2 * p.P_Z))


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
    a = ap.parse_args()
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
