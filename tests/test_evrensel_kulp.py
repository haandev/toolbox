"""Evrensel tavan kulbu: paralel kollu katlanır kulp; 1×1, 2×1, 2×2 gruplarında ortadan taşır."""
import itertools

import pytest
from build123d import Pos
from kutu import params as p
from kutu.montaj import kesisim_hacmi, kutu

_KULP = ("kulp_ayagi", "kulp_kolu", "kulp_cubugu")


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2)])
def test_kulplu_evrensel_tavan_cakismaz(nx, ny):
    k = kutu(nx, ny, 1, tavan="evrensel", kulp=True)
    assert sum(1 for y in k if y.tur == "kulp_cubugu") == 1
    assert sum(1 for y in k if y.tur == "kulp_ayagi") == 2
    assert sum(1 for y in k if y.tur == "kulp_kolu") == 4
    for a, b in itertools.combinations(k, 2):
        assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2)])
def test_katli_kulp_kilit_yuzunun_altinda(nx, ny):
    k = kutu(nx, ny, 1, tavan="evrensel", kulp=True)
    for y in k:
        if y.tur in _KULP:
            assert y.parca.bounding_box().max.Z < p.P_Z - p.GAP, y.ad
            assert y.parca.bounding_box().min.Z > p.P_Z - p.GAP - p.KAPAK_H - 1e-6, y.ad   # sarkmaz


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2)])
def test_acik_kulp_grup_merkezinin_ustunde(nx, ny):
    k = kutu(nx, ny, 1, tavan="evrensel", kulp=True, kulp_acik=True)
    cubuk = next(y for y in k if y.tur == "kulp_cubugu").parca.bounding_box()
    assert cubuk.center().X == pytest.approx(nx * p.P_XY / 2, abs=0.01)
    assert cubuk.center().Y == pytest.approx(ny * p.P_XY / 2, abs=0.01)
    assert cubuk.min.Z > p.P_Z + 15                       # parmak boşluğu
    for a, b in itertools.combinations(k, 2):
        assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 2)])
def test_katli_kulplu_kutunun_ustune_istif(nx, ny):
    alt = kutu(nx, ny, 1, tavan="evrensel", kulp=True)
    ust = [type(y)(y.ad, y.tur, Pos(0, 0, p.P_Z) * y.parca, y.patlat) for y in kutu(nx, ny, 1)]
    kulp = [y for y in alt if y.tur in _KULP]
    assert sum(kesisim_hacmi(a.parca, b.parca) for a in kulp for b in ust) < 1e-3


def test_desteklenmeyen_grupta_kulp_yok():
    k = kutu(3, 1, 1, tavan="evrensel", kulp=True)                # tek grup 3×1
    assert not [y for y in k if y.tur in _KULP]
    k = kutu(3, 1, 1, tavan="evrensel", kulp=True, kapak_gruplari=[(0, 0, 2, 1), (2, 0, 1, 1)])
    assert sum(1 for y in k if y.tur == "kulp_cubugu") == 2
