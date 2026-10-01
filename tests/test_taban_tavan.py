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
    # yerel z = 0 kutunun nominal üstü; köşe tutucuları ERKEK_H taşar
    assert b.max.Z == pytest.approx(p.ERKEK_H - p.GAP)


def test_kose_tutuculari_disi_yuvaya_oturur():
    # her node'un köşesinde tutucu var, dış yüzü çerçeve içinden FIT içeride
    t = tavan(1, 1)
    a = p.K + p.FIT
    kose = Pos(a, a, 0) * Box(p.WALL, p.WALL, p.ERKEK_H - p.GAP - 0.1, align=MIN3)
    assert hacim(t & kose) == pytest.approx(p.WALL * p.WALL * (p.ERKEK_H - p.GAP - 0.1), rel=1e-3)
    disari = Pos(p.K, p.K, 0) * Box(p.FIT - 0.01, _IC, p.ERKEK_H, align=MIN3)
    assert hacim(t & disari) == pytest.approx(0, abs=1e-6)


def test_taban_kaburgalari_bilezik_bandinda_kisa():
    bant = p.WALL + 2 * p.FIT
    derin = p.ERKEK_H + p.FIT
    sonda = Pos(p.K, p.K, p.GAP) * Box(_IC, bant, derin, align=MIN3)
    assert hacim(karo_taban() & sonda) == pytest.approx(0, abs=1e-6)


def test_taban_kilit_yuzunden_tasmaz():
    assert karo_taban().bounding_box().min.Z == pytest.approx(p.GAP)
