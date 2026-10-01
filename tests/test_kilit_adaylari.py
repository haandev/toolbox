import pytest
from build123d import Pos, Rot
from kutu.kilit.adaylar import ADAYLAR, PED, eslesik
from kutu.montaj import kesisim_hacmi


@pytest.mark.parametrize("ad", list(ADAYLAR))
def test_aday_gecerli(ad):
    assert ADAYLAR[ad]().is_valid


@pytest.mark.parametrize("ad", list(ADAYLAR))
def test_kendi_kopyasiyla_cakismadan_eslesir(ad):
    a, b = eslesik(ad)
    assert kesisim_hacmi(a, b) < 1e-3


@pytest.mark.parametrize("ad", list(ADAYLAR))
def test_eslesince_yuzler_degiyor(ad):
    a, b = eslesik(ad)
    # pedler arasında boşluk yok: B'nin ped yüzü A'nın ped yüzüne oturur
    assert a.distance_to(b) == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("ad", list(ADAYLAR))
def test_birbirine_gecmis(ad):
    # B, ped yüzünün altına iner: özellikler karşı tarafa girmiş olmalı
    a, b = eslesik(ad)
    assert b.bounding_box().min.Z < PED[2] - 1


def test_pim_90_derece_donuk_de_eslesir():
    a, b = eslesik("pim")
    b90 = Rot(0, 0, 90) * b
    assert kesisim_hacmi(a, b90) < 1e-3
