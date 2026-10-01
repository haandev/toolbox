import pytest
from build123d import Align, Box, Cylinder, Pos, Rot
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva_y
from kutu.parts.karo import delik_noktalari, karo_taban

from conftest import hacim


@pytest.fixture(scope="module")
def kr():
    return karo_taban()


def test_gecerli_kati(kr):
    assert kr.is_valid


def test_dis_olculer(kr):
    b = kr.bounding_box()
    assert b.size.X == pytest.approx(p.P_XY - 2 * p.GAP)
    assert b.size.Y == pytest.approx(p.P_XY - 2 * p.GAP)
    assert b.min.Z == pytest.approx(p.GAP)
    assert b.max.Z == pytest.approx(p.T + p.DURDURUCU_H)   # çerçeve üstünde çekmece durdurucusu


def test_guverte_wall_kalinliginda(kr):
    c = p.P_XY / 2
    sonda = Pos(c - 5, c - 5, 0) * Box(10, 10, p.T, align=MIN3)
    assert hacim(kr & sonda) == pytest.approx(10 * 10 * p.WALL, rel=1e-3)


@pytest.mark.parametrize("aci", [0, 90, 180, 270])
def test_dort_kenarda_oluk(kr, aci):
    y0, y1 = yuva_y()
    oluk = Pos(p.K, y0, p.T - p.DIL_V) * Box(p.P_XY - 2 * p.K, y1 - y0, p.DIL_V, align=MIN3)
    c = p.P_XY / 2
    oluk = Pos(c, c, 0) * Rot(0, 0, aci) * Pos(-c, -c, 0) * oluk
    assert hacim(kr & oluk) == pytest.approx(0, abs=1e-6)


def test_delik_noktalari_simetrik():
    n = delik_noktalari()
    assert len(n) == 12
    c = p.P_XY / 2
    kume = {(round(x, 3), round(y, 3)) for x, y in n}
    for x, y in n:
        # 90° döndürünce yine bir delik noktası
        assert (round(c - (y - c), 3), round(c + (x - c), 3)) in kume
        # y'de aynalayınca (tavan olarak ters çevirme) yine bir delik noktası
        assert (round(x, 3), round(p.P_XY - y, 3)) in kume


def test_delikler_acik(kr):
    for x, y in delik_noktalari():
        sonda = Pos(x, y, 0) * Cylinder(0.5, p.T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        assert hacim(kr & sonda) == pytest.approx(0, abs=1e-6)
