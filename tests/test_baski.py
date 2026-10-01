"""Baskı için bölme: tavan modülü node boyunda parçalara, kapak parçaları papyon kamla birleşir."""
import itertools

import pytest
from build123d import Pos
from kutu.baski import TABLA, kulp_baski_parcalari, modul_baski_parcalari
from kutu.montaj import kesisim_hacmi
from kutu.parts.kulp import kulp
from kutu.parts.tavan import cerceve, kapak


@pytest.mark.parametrize("mx,my", [(1, 1), (2, 1), (1, 2), (2, 2)])
def test_parcalar_tablaya_sigar_ve_cakismaz(mx, my):
    parcalar = modul_baski_parcalari(mx, my)
    for ad, tur, s in parcalar:
        b = s.bounding_box()
        assert max(b.size.X, b.size.Y) <= TABLA, ad
    for (a1, _, s1), (a2, _, s2) in itertools.combinations(parcalar, 2):
        assert kesisim_hacmi(s1, s2) < 1e-3, f"{a1} / {a2}"


@pytest.mark.parametrize("mx,my", [(2, 1), (1, 2), (2, 2)])
def test_parcalar_tek_parcayla_uyumlu(mx, my):
    parcalar = modul_baski_parcalari(mx, my)
    for tur, ana in (("cerceve", cerceve(mx, my)), ("kapak", kapak(mx, my))):
        toplam = sum(s.volume for _, t, s in parcalar if t == tur)
        assert 0.97 * ana.volume <= toplam <= ana.volume + 1e-6


@pytest.mark.parametrize("mx,my", [(2, 1), (1, 2)])
def test_kapak_parcalari_kamla_kilitli(mx, my):
    parcalar = modul_baski_parcalari(mx, my)
    kamlar = [s for _, t, s in parcalar if t == "papyon_kapak"]
    assert len(kamlar) >= 2
    ikinci = [s for a, t, s in parcalar if t == "kapak" and a.endswith("_1")][0]
    kayik = Pos(1.0, 0, 0) * ikinci if mx == 2 else Pos(0, 1.0, 0) * ikinci
    assert sum(kesisim_hacmi(kayik, k) for k in kamlar) > 1


def test_1x1_modul_bolunmez():
    parcalar = modul_baski_parcalari(1, 1)
    assert sorted(t for _, t, _ in parcalar) == ["cerceve", "kapak"]


def test_2x_kulp_uc_parca_ve_cubuk():
    parcalar = kulp_baski_parcalari(2)
    assert sorted(t for _, t, _ in parcalar) == ["kulp_cubugu", "kulp_ucu", "kulp_ucu"]
    for ad, _, s in parcalar:
        if ad != "kulp_cubugu":
            b = s.bounding_box()
            assert max(b.size.X, b.size.Y) <= TABLA
    for (a1, _, s1), (a2, _, s2) in itertools.combinations(parcalar, 2):
        assert kesisim_hacmi(s1, s2) < 1e-3, f"{a1} / {a2}"
    # birleşik kulp, tek parça kulbun zarfı içinde
    b0 = kulp(2).bounding_box()
    for _, _, s in parcalar:
        b = s.bounding_box()
        assert b.min.X >= b0.min.X - 1e-6 and b.max.X <= b0.max.X + 1e-6
        assert b.min.Z >= b0.min.Z - 1e-6 and b.max.Z <= b0.max.Z + 1e-6
