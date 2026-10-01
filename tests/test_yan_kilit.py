"""Yatay yan raylar: panel dil/oluk, köşe-kıskaç dış olukları, montaj yön kuralı, komşu kutular."""
import itertools

import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.yan_ray import OLUK_DERIN
from kutu.montaj import kesisim_hacmi, kutu
from kutu.parts.kiskac import kiskac
from kutu.parts.kose import kose
from kutu.parts.panel import panel

from conftest import hacim


def _bant(x0, x1, v, y0=p.GAP, derin=OLUK_DERIN - 0.05, h=p.RAY_H):
    return Pos(x0, y0, v - h / 2) * Box(x1 - x0, derin, h, align=MIN3)


def test_panel_dil_kutu_yuzunu_asar():
    assert panel().bounding_box().min.Y == pytest.approx(p.GAP - p.RAY_T)


def test_panel_v1_dil_v2_oluk():
    u = p.U / 2 - 1
    dil = Pos(-u, p.GAP - p.RAY_T, p.RAY_V1 - p.RAY_H / 2) * Box(2 * u, p.RAY_T, p.RAY_H, align=MIN3)
    assert hacim(panel() & dil) == pytest.approx(2 * u * p.RAY_T * p.RAY_H, rel=1e-3)
    assert hacim(panel() & _bant(-u, u, p.RAY_V2)) == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("v", [p.RAY_V1, p.RAY_V2])
def test_kose_iki_dis_yuzunde_oluk(v):
    a, b = 6.0, p.K - 1
    guney = _bant(a, b, v)
    bati = Pos(p.GAP, a, v - p.RAY_H / 2) * Box(OLUK_DERIN - 0.05, b - a, p.RAY_H, align=MIN3)
    assert hacim(kose() & guney) == pytest.approx(0, abs=1e-6)
    assert hacim(kose() & bati) == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("v", [p.RAY_V1, p.RAY_V2])
def test_kiskac_dis_yuzunde_oluk(v):
    assert hacim(kiskac() & _bant(-p.K + 0.5, p.K - 0.5, v)) == pytest.approx(0, abs=1e-6)


def _komsu(a, b, dx, dy, dz=0.0):
    b = [type(y)(y.ad, y.tur, Pos(dx, dy, dz) * y.parca, y.patlat) for y in b]
    for x, y in itertools.product(a, b):
        assert kesisim_hacmi(x.parca, y.parca) < 1e-3, f"{x.ad} / {y.ad}"
    return b


def test_yan_yana_kutular_raylarla_eslesir():
    a = kutu(1, 1, 1)
    b = _komsu(a, kutu(1, 1, 1), p.P_XY, 0)
    pa = next(y for y in a if y.ad.endswith("panel_d100"))
    pb = next(y for y in b if y.ad.endswith("panel_b100"))
    assert pa.parca.distance_to(pb.parca) == pytest.approx(p.FIT, abs=1e-3)


def test_arka_arkaya_kutular_raylarla_eslesir():
    a = kutu(1, 1, 1)
    _komsu(a, kutu(1, 1, 1), 0, p.P_XY)


@pytest.mark.parametrize("dy", [-60.0, -140.0, -200.0, -260.0, -340.0])
def test_komsu_iki_derin_kutunun_yaninda_kayar(dy):
    # 1×2 kutunun doğu yüzünde köşe + kıskaç + köşe; komşu dili hepsinin oluğundan geçer
    a = kutu(1, 2, 1)
    _komsu(a, kutu(1, 1, 1), p.P_XY, p.P_XY + dy)


def test_komsu_raylari_dikeyde_tutar():
    a = kutu(1, 1, 1)
    b = [type(y)(y.ad, y.tur, Pos(p.P_XY, 0, -1.0) * y.parca, y.patlat) for y in kutu(1, 1, 1)]
    pa = next(y for y in a if y.ad.endswith("panel_d100"))
    pb = next(y for y in b if y.ad.endswith("panel_b100"))
    assert kesisim_hacmi(pa.parca, pb.parca) > 1
