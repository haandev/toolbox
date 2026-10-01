"""Açılır kapak: çerçeve + menteşeli kapak + kilitli mandal."""
import itertools

import pytest
from build123d import Pos
from kutu import params as p
from functools import partial

from kutu.montaj import kutu as _kutu, kapak_ac, kesisim_hacmi

kutu = partial(_kutu, tavan="modul")   # bu dosya modül tavanını sınar

_KAPAK = ("kapak", "kapak_mandal", "kulp")


def _gruplar(k):
    ust = [y for y in k if y.tur in _KAPAK]
    govde = [y for y in k if y.tur not in _KAPAK]
    return ust, govde


def _cakisma(a, b):
    return sum(kesisim_hacmi(x.parca, y.parca) for x in a for y in b)


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2)])
def test_kapali_kilitli_cakismaz(nx, ny):
    k = kutu(nx, ny, 1, kulp=True)
    s = {}
    for y in k:
        s[y.tur] = s.get(y.tur, 0) + 1
    assert s["cerceve"] == 1 and s["kapak"] == 1 and s["kapak_mandal"] == nx
    for a, b in itertools.combinations(k, 2):
        assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


@pytest.mark.parametrize("nx", [1, 2])
def test_kilitliyken_kapak_kalkmaz(nx):
    ust, govde = _gruplar(kutu(nx, 1, 1, kulp=True))
    kalkmis = [type(y)(y.ad, y.tur, Pos(0, 0, 1.0) * y.parca, y.patlat) for y in ust]
    cerceve = [y for y in govde if y.tur == "cerceve"]
    assert _cakisma(kalkmis, cerceve) > 1


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1)])
@pytest.mark.parametrize("aci", [2, 10, 30, 60, 90, 100])
def test_mandal_acikken_kapak_acilir(nx, ny, aci):
    k = kutu(nx, ny, 1, kulp=True, kapak_mandal_acik=True)
    ust, govde = _gruplar(k)
    acik = kapak_ac(ust, ny, 1, aci)
    assert _cakisma(acik, govde) < 1e-3


def test_90_derece_acik_kapak_arkaya_ray_yuksekligi_kadar_tasar():
    k = kutu(1, 1, 1, kulp=True, kapak_mandal_acik=True)
    ust, _ = _gruplar(k)
    kapak = next(y for y in kapak_ac(ust, 1, 1, 90) if y.tur == "kapak")
    assert kapak.parca.bounding_box().max.Y <= p.P_XY + p.T_BAS_Z1 + 0.01


@pytest.mark.parametrize("aci", [0.5, 1.0])
def test_mandal_kapaliyken_kapak_acilmaz(aci):
    # çakışma testi sürekli hareketi değil konumu sınar: ilk derecede kanca çıkıntıya dayanır
    k = kutu(1, 1, 1, kulp=True)
    ust, govde = _gruplar(k)
    acik = kapak_ac(ust, 1, 1, aci)
    assert _cakisma(acik, govde) > 1
