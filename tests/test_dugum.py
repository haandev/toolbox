import pytest
from build123d import Align, Box, Cylinder, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva_y
from kutu.parts.kiskac import kiskac_dugumu
from kutu.parts.kose import kose_dugumu

from conftest import hacim

Z0, Z1 = p.T + p.H, p.T + p.H + 2 * p.T   # iki kat arası bant: 90..110


def _delik(x, y):
    return Pos(x, y, Z0) * Cylinder(0.5, 2 * p.T, align=(Align.CENTER, Align.CENTER, Align.MIN))


def test_kose_dugumu_olculer():
    d = kose_dugumu()
    assert d.is_valid
    b = d.bounding_box()
    assert (b.min.X, b.max.X) == pytest.approx((p.GAP, p.K))
    assert (b.min.Z, b.max.Z) == pytest.approx((Z0, Z1))


def test_kose_dugumu_kanallar_ve_delik():
    d = kose_dugumu()
    y0, y1 = yuva_y()
    guney = Pos(p.K - p.DIL, y0, Z0) * Box(p.DIL, y1 - y0, 2 * p.T, align=MIN3)
    bati = Pos(y0, p.K - p.DIL, Z0) * Box(y1 - y0, p.DIL, 2 * p.T, align=MIN3)
    assert hacim(d & guney) == pytest.approx(0, abs=1e-6)
    assert hacim(d & bati) == pytest.approx(0, abs=1e-6)
    assert hacim(d & _delik(p.KOSE_KULE, p.KOSE_KULE)) == pytest.approx(0, abs=1e-6)


def test_kiskac_dugumu_olculer_ve_delikler():
    d = kiskac_dugumu()
    assert d.is_valid
    b = d.bounding_box()
    assert (b.min.X, b.max.X) == pytest.approx((-p.K, p.K))
    assert (b.min.Z, b.max.Z) == pytest.approx((Z0, Z1))
    m = (p.CEP_IC + p.K - p.WALL) / 2
    for x in (-p.KISKAC_KULE_X, p.KISKAC_KULE_X):
        assert hacim(d & _delik(x, m)) == pytest.approx(0, abs=1e-6)
