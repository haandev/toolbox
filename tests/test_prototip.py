import pytest
from build123d import Pos
from kutu import params as p
from kutu.prototip import (FIT_DEGERLERI, dil_kuponu, kanal_kuponu, kule_kuponu,
                           kuponlari_aktar)

from conftest import hacim


@pytest.mark.parametrize("fit", FIT_DEGERLERI)
def test_kanal_kuponu_gecerli(fit):
    assert kanal_kuponu(fit).is_valid


def test_bosluk_arttikca_hacim_azalir():
    hacimler = [kanal_kuponu(f).volume for f in FIT_DEGERLERI]
    assert hacimler == sorted(hacimler, reverse=True)


@pytest.mark.parametrize("fit", FIT_DEGERLERI)
def test_dil_yarikta_fit_boslugu(fit):
    kanal = kanal_kuponu(fit)
    # dil yarığın ortasına, dibe fit kadar mesafeyle oturtulur
    dil = Pos(10 - p.WALL / 2, 12 - p.DIL, 0) * dil_kuponu()
    assert hacim(kanal & dil) == pytest.approx(0, abs=1e-6)
    assert kanal.distance_to(dil) == pytest.approx(fit, abs=1e-3)


def test_kule_kuponu_gecerli():
    k = kule_kuponu()
    assert k.is_valid
    assert k.bounding_box().max.Z > p.WALL


def test_kuponlari_aktar(tmp_path):
    dosyalar = kuponlari_aktar(tmp_path)
    assert len(dosyalar) == len(FIT_DEGERLERI) + 2
    for d in dosyalar:
        assert d.stat().st_size > 0
