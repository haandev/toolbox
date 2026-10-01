"""Tolerans kalibrasyonu için küçük baskı parçaları."""
from pathlib import Path

from build123d import Box, Part, Pos, Rot, export_stl

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kule import kule

FIT_DEGERLERI = (0.1, 0.2, 0.3, 0.4)
_BLOK = (20.0, 12.0, 15.0)
_CENTIK = 1.5


def kanal_kuponu(fit: float) -> Part:
    bx, by, bz = _BLOK
    blok = Box(bx, by, bz, align=MIN3)
    gen = p.WALL + 2 * fit
    blok -= Pos(bx / 2 - gen / 2, by - p.DIL - fit, 0) * Box(gen, p.DIL + fit, bz, align=MIN3)
    # baskıdan sonra ayırt etmek için sıra numarası kadar çentik (y=0 yüzünün üst kenarı)
    sira = FIT_DEGERLERI.index(fit) + 1 if fit in FIT_DEGERLERI else 0
    for i in range(sira):
        blok -= Pos(1 + i * 2 * _CENTIK, 0, bz - _CENTIK) * Box(_CENTIK, _CENTIK, _CENTIK, align=MIN3)
    return blok


def dil_kuponu() -> Part:
    return Box(p.WALL, p.DIL + 10, _BLOK[2], align=MIN3)


def kule_kuponu() -> Part:
    plaka = Box(20, 20, p.WALL, align=MIN3)
    boy = p.CEP_BOY / 2
    return plaka + Pos(10, 10, p.WALL + boy) * Rot(180, 0, 0) * kule(boy)


def kuponlari_aktar(cikti: Path) -> list[Path]:
    klasor = cikti / "prototip"
    klasor.mkdir(parents=True, exist_ok=True)
    dosyalar = []
    for f in FIT_DEGERLERI:
        d = klasor / f"kanal_fit_{f:.1f}.stl"
        export_stl(kanal_kuponu(f), str(d))
        dosyalar.append(d)
    for ad, parca in (("dil", dil_kuponu()), ("kule", kule_kuponu())):
        d = klasor / f"{ad}.stl"
        export_stl(parca, str(d))
        dosyalar.append(d)
    return dosyalar


if __name__ == "__main__":
    for d in kuponlari_aktar(Path("out")):
        print(d)
