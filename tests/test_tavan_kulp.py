"""Tek parça tavan + içine gömülü 1×/2×/3× kulp."""
import itertools

import pytest
from build123d import Pos
from kutu import params as p
from kutu.montaj import kesisim_hacmi, kutu
from kutu.parts.kulp import kulp


@pytest.mark.parametrize("n", [1, 2, 3])
def test_kulp_gecerli(n):
    assert kulp(n).is_valid


@pytest.mark.parametrize("nx,ny,n", [(1, 1, 1), (2, 1, 2), (3, 1, 3), (2, 2, 2), (4, 1, 3)])
def test_kulplu_kutu_cakismaz(nx, ny, n):
    k = kutu(nx, ny, 1, kulp=True)
    kp = [y for y in k if y.tur == "kulp"]
    assert len(kp) == 1 and kp[0].ad == f"kulp_{n}x"
    for a, b in itertools.combinations(k, 2):
        assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2)])
def test_kulp_katliyken_kilit_yuzunun_altinda(nx, ny):
    k = kutu(nx, ny, 1, kulp=True)
    kp = next(y for y in k if y.tur == "kulp")
    assert kp.parca.bounding_box().max.Z < p.P_Z - p.GAP


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2)])
def test_kulp_ortada(nx, ny):
    k = kutu(nx, ny, 1, kulp=True)
    c = next(y for y in k if y.tur == "kulp").parca.bounding_box().center()
    assert c.X == pytest.approx(nx * p.P_XY / 2, abs=0.5)


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2)])
def test_kulp_acikken_cakismaz_ve_yukarida(nx, ny):
    k = kutu(nx, ny, 1, kulp=True, kulp_acik=True)
    kp = next(y for y in k if y.tur == "kulp")
    assert kp.parca.bounding_box().max.Z > p.P_Z + p.T_BAS_Z1 + 20
    for y in k:
        if y is not kp:
            assert kesisim_hacmi(kp.parca, y.parca) < 1e-3, y.ad


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (3, 1), (2, 2)])
def test_kulplu_kutunun_ustune_istif(nx, ny):
    alt = kutu(nx, ny, 1, kulp=True)
    ust = [type(y)(y.ad, y.tur, Pos(0, 0, p.P_Z) * y.parca, y.patlat) for y in kutu(nx, ny, 1)]
    for a in alt:
        for b in ust:
            if a.tur in ("kulp", "kapak", "kapak_mandal", "cerceve"):
                assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


def test_kulp_kesiti_14mm():
    assert kulp(2).bounding_box().size.Z == pytest.approx(14.0)
