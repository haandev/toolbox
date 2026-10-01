"""Parçaları node ızgarasına yerleştirir: kutu(nx, ny, nz)."""
from dataclasses import dataclass

from build123d import Part, Pos, Rot

from kutu import params as p
from kutu.parts.karo import karo
from kutu.parts.kiskac import kiskac
from kutu.parts.kose import kose
from kutu.parts.panel import panel


@dataclass
class Yerlesim:
    ad: str
    tur: str
    parca: Part
    patlat: tuple[float, float, float]


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


def kutu(nx: int, ny: int, nz: int = 1) -> list[Yerlesim]:
    W, D = nx * p.P_XY, ny * p.P_XY
    out: list[Yerlesim] = []

    def ekle(ad: str, tur: str, parca: Part, zb: float) -> None:
        c = parca.bounding_box().center()
        if tur == "karo":
            yon = (0, 0, _isaret(c.Z - (zb + p.P_Z / 2)))
        else:
            yon = (_isaret(c.X - W / 2), _isaret(c.Y - D / 2), 0)
        out.append(Yerlesim(ad, tur, parca, yon))

    for kat in range(nz):
        zb = kat * p.P_Z
        for i in range(nx):
            for j in range(ny):
                x0, y0 = i * p.P_XY, j * p.P_XY
                ekle(f"k{kat}_taban_{i}{j}", "karo", Pos(x0, y0, zb) * karo(), zb)
                ekle(f"k{kat}_tavan_{i}{j}", "karo",
                     Pos(x0, y0 + p.P_XY, zb + p.P_Z) * Rot(180, 0, 0) * karo(), zb)

        for ad, yer in (
            ("gb", Pos(0, 0, zb)),
            ("gd", Pos(W, 0, zb) * Rot(0, 0, 90)),
            ("kd", Pos(W, D, zb) * Rot(0, 0, 180)),
            ("kb", Pos(0, D, zb) * Rot(0, 0, -90)),
        ):
            ekle(f"k{kat}_kose_{ad}", "kose", yer * kose(), zb)

        def duvar(tur: str, parca: Part, x_listesi, y_listesi) -> None:
            for x in x_listesi:
                ekle(f"k{kat}_{tur}_g{x:g}", tur, Pos(x, 0, zb) * parca, zb)
                ekle(f"k{kat}_{tur}_k{x:g}", tur, Pos(x, D, zb) * Rot(0, 0, 180) * parca, zb)
            for y in y_listesi:
                ekle(f"k{kat}_{tur}_b{y:g}", tur, Pos(0, y, zb) * Rot(0, 0, -90) * parca, zb)
                ekle(f"k{kat}_{tur}_d{y:g}", tur, Pos(W, y, zb) * Rot(0, 0, 90) * parca, zb)

        orta = p.P_XY / 2
        duvar("panel", panel(),
              [orta + i * p.P_XY for i in range(nx)],
              [orta + j * p.P_XY for j in range(ny)])
        duvar("kiskac", kiskac(),
              [i * p.P_XY for i in range(1, nx)],
              [j * p.P_XY for j in range(1, ny)])
    return out
