import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.parts.karo import karo_taban
from kutu.parts.tavan import tavan

from conftest import hacim

_IC = p.P_XY - 2 * p.K          # tabanın çerçeve içi (dişi yuva) ölçüsü


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (3, 1), (2, 2)])
def test_tavan_tek_parca_olculer(nx, ny):
    t = tavan(nx, ny)
    assert t.is_valid
    b = t.bounding_box()
    assert b.size.X == pytest.approx(p.kutu_dis(nx, p.P_XY))
    assert b.size.Y == pytest.approx(p.kutu_dis(ny, p.P_XY))
    # yerel z = 0 kutunun nominal üstü; kılavuz raylar KILAVUZ_H taşar
    assert b.max.Z == pytest.approx(p.KILAVUZ_H - p.GAP)


@pytest.mark.parametrize("ny", [1, 2])
def test_kilavuz_raylar_onden_arkaya(ny):
    t = tavan(1, ny)
    a, h = p.K + p.FIT, p.KILAVUZ_H - p.GAP - 0.1
    D = ny * p.P_XY
    for x in (a, p.P_XY - a - p.WALL):
        ray = Pos(x, 2 * p.KILAVUZ_H, 0) * Box(p.WALL, D - 4 * p.KILAVUZ_H, h, align=MIN3)
        assert hacim(t & ray) == pytest.approx(p.WALL * (D - 4 * p.KILAVUZ_H) * h, rel=1e-3)
    # node ortasında kilit yüzünün üstü boş (eski tutucu yok)
    orta = Pos(p.K + 10, p.K + 10, 0) * Box(_IC - 20, 30, p.KILAVUZ_H, align=MIN3)
    assert hacim(t & orta) == pytest.approx(0, abs=1e-6)


def test_taban_kenarlarinda_kilavuz_centigi():
    g, h = p.WALL + 2 * p.FIT, p.KILAVUZ_H + p.FIT
    for x in (p.K, p.P_XY - p.K - g):
        sonda = Pos(x, p.GAP, p.GAP) * Box(g, p.K - p.GAP, h - 0.01, align=MIN3)
        assert hacim(karo_taban() & sonda) == pytest.approx(0, abs=1e-6)


def test_taban_kaburgalari_bilezik_bandinda_kisa():
    bant = p.WALL + 2 * p.FIT
    derin = p.KILAVUZ_H + p.FIT
    sonda = Pos(p.K, p.K, p.GAP) * Box(_IC, bant, derin, align=MIN3)
    assert hacim(karo_taban() & sonda) == pytest.approx(0, abs=1e-6)


def test_taban_kilit_yuzunden_tasmaz():
    assert karo_taban().bounding_box().min.Z == pytest.approx(p.GAP)
