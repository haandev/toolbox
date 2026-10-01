import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y, yuva_y
from kutu.parts.yatay_kiskac import yatay_kiskac

from conftest import hacim

Z0, Z1 = p.T + p.H, p.T + p.H + 2 * p.T


@pytest.fixture(scope="module")
def yk():
    return yatay_kiskac()


def test_gecerli_ve_olculer(yk):
    assert yk.is_valid
    b = yk.bounding_box()
    assert b.size.X == pytest.approx(p.PANEL_L)        # gövde U + iki uçta DIL dil
    assert (b.min.Z, b.max.Z) == pytest.approx((Z0, Z1))
    assert (b.min.Y, b.max.Y) == pytest.approx((p.GAP, p.K))


@pytest.mark.parametrize("alt", [True, False])
def test_alt_ve_ust_oluk(yk, alt):
    y0, y1 = yuva_y()
    z = Z0 if alt else Z1 - p.DIL_V
    oluk = Pos(-p.U / 2, y0, z) * Box(p.U, y1 - y0, p.DIL_V, align=MIN3)
    assert hacim(yk & oluk) == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("taraf", [-1, 1])
def test_uclarda_dil_wall_kalinliginda(yk, taraf):
    py0, _ = panel_y()
    x0 = p.U / 2 if taraf > 0 else -p.U / 2 - p.DIL
    bolge = Pos(x0, 0, Z0) * Box(p.DIL, p.K, 2 * p.T, align=MIN3)
    # dil, düğüm kanalında alt ve üst panel dillerinin arasında kalır (FIT boşluklu)
    dil_h = 2 * p.T - 2 * (p.DIL_V + p.FIT)
    assert hacim(yk & bolge) == pytest.approx(p.DIL * p.WALL * dil_h, rel=1e-3)


def test_ici_oyuk(yk):
    dolu = p.U * (p.K - p.GAP) * 2 * p.T
    assert yk.volume < 0.6 * dolu
