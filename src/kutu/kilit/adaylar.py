"""Cinsiyetsiz kilit adayları — karşılaştırma örnekleri.

Her aday 60×60 bir ped üzerindedir; ped yüzü z = PED[2]. Eş parça (B), A'nın
kendisinin ters çevrilmiş hâlidir: cinsiyetsizlik geometride doğrudan sınanır.
"""
from math import cos, radians, sin

from build123d import (Align, Box, Cylinder, Part, Plane, Polygon, Pos, Rot,
                       extrude)

from kutu import params as p

PED = (60.0, 60.0, 6.0)
_ORTA = (Align.CENTER, Align.CENTER, Align.MIN)
_F = p.FIT


def _ped() -> Part:
    return Box(*PED, align=_ORTA)


def _yamuk(xc: float, alt_gen: float, ust_gen: float, z0: float, z1: float, boy: float) -> Part:
    """XZ düzleminde yamuk kesit, y boyunca simetrik uzatılmış."""
    noktalar = [(xc - alt_gen / 2, z0), (xc + alt_gen / 2, z0),
                (xc + ust_gen / 2, z1), (xc - ust_gen / 2, z1)]
    return extrude(Plane.XZ * Polygon(*noktalar, align=None), amount=boy / 2, both=True)


# --- 1. Kırlangıç çifti: solda dil, sağda yuva; y boyunca kayarak kilitlenir ---
def kirlangic() -> Part:
    z = PED[2]
    dil = _yamuk(-15, 10, 14, z, z + 4, PED[1])
    yuva = _yamuk(15, 14 + 2 * _F, 10 + 2 * _F, z - 4 - _F, z, PED[1] + 2)
    return _ped() + dil - yuva


# --- 2. Dönel simetrik pim/delik: 90° döndürünce de eşleşir ---
_R = 18.0
_PIM_D = 8.0


def pim() -> Part:
    z = PED[2]
    govde = _ped()
    for k in range(4):
        a = radians(22.5 + 90 * k)
        govde += Pos(_R * cos(a), _R * sin(a), z) * Cylinder(_PIM_D / 2, z, align=_ORTA)
        b = radians(67.5 + 90 * k)
        govde -= Pos(_R * cos(b), _R * sin(b), 0) * Cylinder(_PIM_D / 2 + _F, z, align=_ORTA)
    return govde


# --- 3. Kanca: solda +x'e bakan kanca, sağda karşı kancanın penceresi; x'te kayarak kilitlenir ---
_KG = 20.0   # kanca genişliği (y)


def kanca() -> Part:
    z = PED[2]
    govde = _ped()
    # kanca: gövde (x -20..-16, tam boy) + dudak (x -16..-6, üst yarı)
    govde += Pos(-20, -_KG / 2, z) * Box(4, _KG, z, align=(Align.MIN, Align.MIN, Align.MIN))
    govde += Pos(-16, -_KG / 2, z + z / 2) * Box(10, _KG, z / 2, align=(Align.MIN, Align.MIN, Align.MIN))
    # karşı kanca için pencere (ped yüzünde) ve dudak odası (ped arkasında)
    yg = _KG + 2 * _F
    govde -= Pos(14 - _F, -yg / 2, z / 2 - _F) * Box(14 + 2 * _F, yg, z / 2 + _F + 0.01, align=(Align.MIN, Align.MIN, Align.MIN))
    govde -= Pos(6 - _F, -yg / 2, -0.01) * Box(22 + 2 * _F, yg, z / 2 + _F + 0.01, align=(Align.MIN, Align.MIN, Align.MIN))
    return govde


ADAYLAR = {"kirlangic": kirlangic, "pim": pim, "kanca": kanca}


def eslesik(ad: str) -> tuple[Part, Part]:
    """A ve onun ters çevrilmiş kopyası B, kilitli konumda."""
    a = ADAYLAR[ad]()
    z = 2 * PED[2]
    if ad == "pim":
        b = Pos(0, 0, z) * Rot(180, 0, 0) * a      # X ekseni etrafında çevir
    else:
        b = Pos(0, 0, z) * Rot(0, 180, 0) * a      # Y ekseni etrafında çevir
    return a, b


def aktar(cikti) -> dict:
    """Adayları yan yana önizleme klasörüne yazar (manifest + konumlu STL)."""
    import json
    from pathlib import Path

    from build123d import export_stl

    klasor = Path(cikti) / "kilit"
    klasor.mkdir(parents=True, exist_ok=True)
    for eski in klasor.glob("*.stl"):
        eski.unlink()
    parcalar = []
    aralik = PED[0] + 50
    for i, ad in enumerate(ADAYLAR):
        a, b = eslesik(ad)
        for harf, parca, renk, yon in (("A", a, "#9fb3c8", [0, 0, 0]), ("B", b, "#f39c3d", [0, 0, 1])):
            dosya = f"{ad}_{harf}.stl"
            export_stl(Pos(i * aralik, 0, 0) * parca, str(klasor / dosya))
            parcalar.append({"ad": f"{ad}_{harf}", "tur": f"{ad}", "dosya": dosya, "renk": renk, "patlat": yon})
    w = (len(ADAYLAR) - 1) * aralik
    manifest = {"sahne": {"x0": -PED[0] / 2, "x1": w + PED[0] / 2, "y0": -PED[1] / 2, "y1": PED[1] / 2,
                          "z0": 0, "z1": 2 * PED[2]},
                "parcalar": parcalar, "kilit": []}
    (klasor / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    return manifest


if __name__ == "__main__":
    print(len(aktar("out")["parcalar"]), "parça → out/kilit/manifest.json")
