"""STEP (kalıpçı), STL (prototip) ve önizleme (konumlu STL + manifest) çıktıları."""
import argparse
import json
from pathlib import Path

from build123d import Pos, export_step, export_stl

from kutu import params as p
from kutu.kalip import egimsiz_yuz_sayisi
from kutu.lib.kilit_yeri import kilit_noktalari
from kutu.montaj import kutu
from kutu.parts.karo import karo_taban, karo_tavan
from kutu.parts.kiskac import kiskac, kiskac_dugumu
from kutu.parts.kose import kose, kose_dugumu
from kutu.parts.panel import panel
from kutu.parts.yatay_kiskac import yatay_kiskac

TURLER = {"panel": panel, "kose": kose, "kiskac": kiskac, "taban": karo_taban, "tavan": karo_tavan,
          "yatay_kiskac": yatay_kiskac, "kose_dugumu": kose_dugumu, "kiskac_dugumu": kiskac_dugumu}
CEKME = {"panel": (0, 1, 0), "kose": (0, 0, 1), "kiskac": (0, 0, 1), "taban": (0, 0, 1), "tavan": (0, 0, 1),
         "yatay_kiskac": (0, 1, 0), "kose_dugumu": (0, 0, 1), "kiskac_dugumu": (0, 0, 1)}
RENKLER = {"taban": "#5b6270", "tavan": "#7a8394", "kose": "#f39c3d", "kiskac": "#f1c40f", "panel": "#9fb3c8",
           "yatay_kiskac": "#2ecc9a", "kose_dugumu": "#d35400", "kiskac_dugumu": "#b7950b"}


def disa_aktar(cikti: Path, nx: int, ny: int, nz: int) -> dict:
    for alt in ("step", "stl", "preview"):
        (cikti / alt).mkdir(parents=True, exist_ok=True)

    for tur, fn in TURLER.items():
        parca = fn()
        export_step(parca, str(cikti / "step" / f"{tur}.step"))
        export_stl(parca, str(cikti / "stl" / f"{tur}.stl"))
        print(f"{tur:7s} eğimsiz yüz: {egimsiz_yuz_sayisi(parca, CEKME[tur])}")

    onizleme = cikti / "preview"
    for eski in onizleme.glob("*.stl"):
        eski.unlink()
    parcalar = []
    for y in kutu(nx, ny, nz):
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


def istif_aktar(cikti: Path) -> dict:
    """40×20 kutunun üstünde 200 mm kaydırılmış 20×20 kutu: erkek–dişi istif önizlemesi."""
    klasor = cikti / "istif"
    klasor.mkdir(parents=True, exist_ok=True)
    for eski in klasor.glob("*.stl"):
        eski.unlink()
    parcalar = []
    for on_ek, liste, ust in (("alt", kutu(2, 1, 1), False),
                              ("ust", kutu(1, 1, 1), True)):
        for y in liste:
            parca = Pos(p.P_XY, 0, p.P_Z) * y.parca if ust else y.parca
            dosya = f"{on_ek}_{y.ad}.stl"
            export_stl(parca, str(klasor / dosya))
            yon = [y.patlat[0], y.patlat[1], y.patlat[2] + (2 if ust else 0)]
            parcalar.append({"ad": f"{on_ek}_{y.ad}", "tur": y.tur, "dosya": dosya,
                             "renk": RENKLER[y.tur], "patlat": yon})
    manifest = {"sahne": {"x0": 0, "x1": 2 * p.P_XY, "y0": 0, "y1": p.P_XY, "z0": 0, "z1": 2 * p.P_Z},
                "parcalar": parcalar,
                "kilit": [{"yuz": yuz, "merkez": list(m)} for yuz, m in kilit_noktalari(2, 1, 1)]}
    (klasor / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description="Modüler kutu çıktıları")
    ap.add_argument("--nx", type=int, default=1)
    ap.add_argument("--ny", type=int, default=1)
    ap.add_argument("--nz", type=int, default=1)
    ap.add_argument("--cikti", type=Path, default=Path("out"))
    ap.add_argument("--istif", action="store_true", help="istif önizlemesi (out/istif)")
    a = ap.parse_args()
    if a.istif:
        print(len(istif_aktar(a.cikti)["parcalar"]), "parça → out/istif/manifest.json")
        return
    m = disa_aktar(a.cikti, a.nx, a.ny, a.nz)
    print(f"{len(m['parcalar'])} parça → {a.cikti}/preview/manifest.json")


if __name__ == "__main__":
    main()
