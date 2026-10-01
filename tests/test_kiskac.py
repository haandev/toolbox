import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva_y
from kutu.parts.kiskac import kiskac

from conftest import hacim


@pytest.fixture(scope="module")
def ks():
    return kiskac()


def test_gecerli_kati(ks):
    assert ks.is_valid


def test_dis_olculer(ks):
    b = ks.bounding_box()
    assert b.size.X == pytest.approx(2 * p.K)
    assert b.min.X == pytest.approx(-p.K)
    assert b.min.Y == pytest.approx(p.GAP)
    assert b.max.Y == pytest.approx(p.K)
    assert b.min.Z == pytest.approx(p.T)
    assert b.max.Z == pytest.approx(p.T + p.H)


@pytest.mark.parametrize("taraf", [-1, 1])
def test_iki_yanda_kanal(ks, taraf):
    y0, y1 = yuva_y()
    x0 = p.K - p.DIL if taraf > 0 else -p.K
    sonda = Pos(x0, y0, p.T) * Box(p.DIL, y1 - y0, p.H, align=MIN3)
    assert hacim(ks & sonda) == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("x", [-p.KISKAC_KULE_X, p.KISKAC_KULE_X])
def test_iki_kule_uclarda_acik(ks, x):
    m = (p.CEP_IC + p.K - p.WALL) / 2
    alt = Pos(x - 0.5, m - 0.5, p.T) * Box(1, 1, 3, align=MIN3)
    ust = Pos(x - 0.5, m - 0.5, p.T + p.H - 3) * Box(1, 1, 3, align=MIN3)
    assert hacim(ks & alt) == pytest.approx(0, abs=1e-6)
    assert hacim(ks & ust) == pytest.approx(0, abs=1e-6)
