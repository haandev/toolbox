"""Kilit bölgeleri (bu fazda boş bırakılan hacim) ve kilit noktası ızgarası."""
from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y


def panel_bolgesi() -> Part:
    """Panel yerel çerçevesinde (x merkezli), deri arkasında kaburgasız kalacak hacim."""
    _, y_ic = panel_y()
    return Pos(-p.KILIT_W / 2, y_ic, p.T + (p.H - p.KILIT_H) / 2) * Box(
        p.KILIT_W, p.RIB_D, p.KILIT_H, align=MIN3
    )


def karo_bolgesi() -> Part:
    """Karo yerel çerçevesinde, merkezde kaburgasız kalacak hacim (güverte altı)."""
    a = (p.P_XY - p.KILIT_KARO) / 2
    return Pos(a, a, p.GAP) * Box(p.KILIT_KARO, p.KILIT_KARO, p.T - p.GAP - p.WALL, align=MIN3)


def kilit_noktalari(nx: int, ny: int, nz: int) -> list[tuple[str, tuple[float, float, float]]]:
    W, D, Hh = nx * p.P_XY, ny * p.P_XY, nz * p.P_Z
    hx = p.P_XY / 2
    hz = p.P_Z / 2
    out: list[tuple[str, tuple[float, float, float]]] = []
    for k in range(nz):
        z = hz + k * p.P_Z
        for i in range(nx):
            x = hx + i * p.P_XY
            out.append(("guney", (x, 0, z)))
            out.append(("kuzey", (x, D, z)))
        for j in range(ny):
            y = hx + j * p.P_XY
            out.append(("bati", (0, y, z)))
            out.append(("dogu", (W, y, z)))
    for i in range(nx):
        for j in range(ny):
            x, y = hx + i * p.P_XY, hx + j * p.P_XY
            out.append(("alt", (x, y, 0)))
            out.append(("ust", (x, y, Hh)))
    return out
