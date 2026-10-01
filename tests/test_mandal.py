"""Dikey çekme mandalı: tavandaki kayar kanca, üst kutunun taban karosundaki anahtar deliğine girer."""
import itertools

import pytest
from build123d import Pos, Rot
from kutu import params as p
from kutu.montaj import kesisim_hacmi, kutu


def _kaydir(liste, dx=0.0, dy=0.0, dz=0.0, yer=None):
    yer = yer if yer is not None else Pos(dx, dy, dz)
    return [type(y)(y.ad, y.tur, yer * y.parca, y.patlat) for y in liste]


@pytest.mark.parametrize("nx,ny,adet", [(1, 1, 2), (2, 1, 4), (2, 2, 4)])
def test_mandal_sayisi_ve_cakismasizlik(nx, ny, adet):
    k = kutu(nx, ny, 1, mandal=True)
    m = [y for y in k if y.tur == "mandal"]
    assert len(m) == adet          # ön ve arka yüzde, her node'da bir
    for a, b in itertools.combinations(k, 2):
        assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


def _istif(acik: bool, ust_yer=None, nx=1):
    alt = kutu(nx, 1, 1, mandal=True, mandal_acik=acik)
    ust = kutu(nx, 1, 1)
    yer = ust_yer if ust_yer is not None else Pos(0, 0, p.P_Z)
    return alt, _kaydir(ust, yer=yer)


def _carpisma(alt, ust):
    mandallar = [y for y in alt if y.tur in ("mandal", "tavan")]
    tabanlar = [y for y in ust if y.tur == "taban"]
    return sum(kesisim_hacmi(a.parca, b.parca) for a in mandallar for b in tabanlar)


@pytest.mark.parametrize("acik", [False, True])
def test_istifte_cakismaz(acik):
    alt, ust = _istif(acik)
    assert _carpisma(alt, ust) < 1e-3


def test_kilitliyken_ust_kutu_kalkamaz():
    alt, ust = _istif(False)
    ust_kalkmis = _kaydir(ust, dz=1.0)
    assert _carpisma(alt, ust_kalkmis) > 1


def test_acikken_ust_kutu_serbest_kalkar():
    alt, ust = _istif(True)
    for dz in (1.0, 3.0, 6.0, 10.0):
        assert _carpisma(alt, _kaydir(ust, dz=dz)) < 1e-3, dz


def test_kilitli_kanca_ile_cikinti_arasi_fit():
    alt, ust = _istif(False)
    m = next(y for y in alt if y.tur == "mandal")
    tb = next(y for y in ust if y.tur == "taban")
    assert m.parca.distance_to(tb.parca) == pytest.approx(p.FIT, abs=1e-3)


@pytest.mark.parametrize("aci", [90, 180])
def test_dondurulmus_ust_kutu_da_kilitlenir(aci):
    c = p.P_XY / 2
    yer = Pos(0, 0, p.P_Z) * Pos(c, c, 0) * Rot(0, 0, aci) * Pos(-c, -c, 0)
    alt, ust = _istif(False, ust_yer=yer)
    assert _carpisma(alt, ust) < 1e-3
    assert _carpisma(alt, _kaydir(ust, dz=1.0)) > 1
