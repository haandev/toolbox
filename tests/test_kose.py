import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva_y
from kutu.parts.kose import kose

from conftest import hacim


@pytest.fixture(scope="module")
def k():
    return kose()


def test_gecerli_kati(k):
    assert k.is_valid


def test_dis_olculer(k):
    b = k.bounding_box()
    assert b.min.X == pytest.approx(p.GAP)
    assert b.min.Y == pytest.approx(p.GAP)
    assert b.max.X == pytest.approx(p.K)
    assert b.max.Y == pytest.approx(p.K)
    assert b.min.Z == pytest.approx(p.T)
    assert b.max.Z == pytest.approx(p.T + p.H)


def test_kanallar_bos(k):
    y0, y1 = yuva_y()
    guney = Pos(p.K - p.DIL, y0, p.T) * Box(p.DIL, y1 - y0, p.H, align=MIN3)
    bati = Pos(y0, p.K - p.DIL, p.T) * Box(y1 - y0, p.DIL, p.H, align=MIN3)
    assert hacim(k & guney) == pytest.approx(0, abs=1e-6)
    assert hacim(k & bati) == pytest.approx(0, abs=1e-6)


def test_ici_oyuk(k):
    dolu = (p.K - p.GAP) ** 2 * p.H
    assert k.volume < 0.75 * dolu


def test_vida_delikleri_uclarda_acik(k):
    m = p.KOSE_KULE
    alt = Pos(m - 0.5, m - 0.5, p.T) * Box(1, 1, 3, align=MIN3)
    ust = Pos(m - 0.5, m - 0.5, p.T + p.H - 3) * Box(1, 1, 3, align=MIN3)
    assert hacim(k & alt) == pytest.approx(0, abs=1e-6)
    assert hacim(k & ust) == pytest.approx(0, abs=1e-6)
