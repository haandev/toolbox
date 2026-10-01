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
    # yerel z = 0 kutunun nominal üstü; en yüksek çıkıntı kılavuz ray ya da T kanca başı
    assert b.max.Z == pytest.approx(p.T_BAS_Z1)


def test_taban_kilit_yuzunden_tasmaz():
    assert karo_taban().bounding_box().min.Z == pytest.approx(p.GAP)
