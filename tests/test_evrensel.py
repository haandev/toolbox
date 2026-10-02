"""Evrensel tavan: çerçeve kenar şeritleri (+ sökülebilir iç köprüler), tek tip kapak hücresi, yuva ekleri, gruplar."""
import itertools

import pytest
from build123d import Align, Box, Pos
from kutu import params as p
from kutu.montaj import evrensel_grup_ac, kesisim_hacmi, kutu
from kutu.parts.evrensel import (cerceve_kenari, kam, kapak_hucre, mandal_eki, mentese_cerceve,
                                 mentese_kapak, tapa)

UST = ("kapak_hucre", "kam_kapak", "mentese_kapak", "mandal_eki")
ALT = ("cerceve_kenari", "cerceve_kenari_cepli", "kam_cerceve", "tapa", "mentese_cerceve", "mentese_pimi")


def _say(k, tur):
    return sum(1 for y in k if y.tur == tur)


def _cakisma(a, b):
    return sum(kesisim_hacmi(x.parca, y.parca) for x in a for y in b)


@pytest.mark.parametrize("parca", [cerceve_kenari, kapak_hucre, kam, tapa, mentese_cerceve,
                                   mentese_kapak, mandal_eki])
def test_parcalar_gecerli_ve_tablaya_sigar(parca):
    s = parca()
    assert s.is_valid
    b = s.bounding_box()
    assert max(b.size.X, b.size.Y) <= 256


def _seritler(k):
    return _say(k, "cerceve_kenari") + _say(k, "cerceve_kenari_cepli")


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (1, 2), (2, 2), (3, 2)])
def test_evrensel_tavan_cakismaz_ve_tek_tip(nx, ny):
    k = kutu(nx, ny, 1, tavan="evrensel")
    assert _seritler(k) == 4 * nx * ny and _say(k, "kapak_hucre") == nx * ny
    ic = (nx - 1) * ny + nx * (ny - 1)
    assert _say(k, "kam_cerceve") == 3 * ic and _say(k, "kam_kapak") == 2 * ic   # tek grup; çerçevede kenar ortası da
    for a, b in itertools.combinations(k, 2):
        assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


@pytest.mark.parametrize("nx,ny,gruplar", [(2, 1, None), (2, 2, None), (3, 2, None),
                                           (2, 2, [(0, 0, 2, 1), (0, 1, 2, 1)])])
def test_koprusuz_cakismaz(nx, ny, gruplar):
    k = kutu(nx, ny, 1, tavan="evrensel", kopru=False, kulp=True, kapak_gruplari=gruplar)
    for a, b in itertools.combinations(k, 2):
        assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


def test_koprusuz_tek_kapakta_ic_tamamen_acik():
    nx = ny = 2
    k = kutu(nx, ny, 1, tavan="evrensel", kopru=False)
    assert _seritler(k) == 2 * (nx + ny) and _say(k, "kam_cerceve") == 0
    W = nx * p.P_XY
    acik = Pos(p.K + 0.5, p.K + 0.5, p.P_Z - p.T - 1) * Box(W - 2 * p.K - 1, W - 2 * p.K - 1, p.T + 1,
                                                           align=(Align.MIN, Align.MIN, Align.MIN))
    assert _cakisma([y for y in k if y.tur in ALT], [type(k[0])("a", "a", acik, (0, 0, 0))]) < 1e-3


def test_grup_sinirinda_kopru_kalir():
    k = kutu(2, 2, 1, tavan="evrensel", kopru=False, kapak_gruplari=[(0, 0, 2, 1), (0, 1, 2, 1)])
    assert _seritler(k) == 8 + 4                      # çevre + j = 0/1 ek yerinde sırt sırta iki şerit × 2 node
    assert _say(k, "kam_cerceve") == 2 * 2            # menteşe/mandal yuvası (160) dolu


def test_kamlar_hucreleri_kilitler():
    k = kutu(2, 1, 1, tavan="evrensel")
    sag = next(y for y in k if y.ad == "cerceve_kenari_10_b")
    kamlar = [y for y in k if y.tur == "kam_cerceve"]
    assert sum(kesisim_hacmi(Pos(1.0, 0, 0) * sag.parca, m.parca) for m in kamlar) > 1


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 2)])
def test_kilitliyken_kapak_kalkmaz(nx, ny):
    k = kutu(nx, ny, 1, tavan="evrensel")
    ust = [y for y in k if y.tur in UST]
    alt = [y for y in k if y.tur in ALT]
    assert _cakisma([type(y)(y.ad, y.tur, Pos(0, 0, 1.0) * y.parca, y.patlat) for y in ust], alt) > 1


_IKI = [(0, 0, 2, 1), (0, 1, 2, 1)]


@pytest.mark.parametrize("gruplar,g,aci", [
    (None, 0, 2), (None, 0, 30), (None, 0, 90),
    (_IKI, 1, 30), (_IKI, 1, 90), (_IKI, 0, 2), (_IKI, 0, 30),
])
def test_grup_acilir(gruplar, g, aci):
    k = kutu(2, 2, 1, tavan="evrensel", kapak_gruplari=gruplar, mandal_acik=True)
    acik = evrensel_grup_ac(k, g, aci, 2, 2, 1, gruplar)
    assert acik
    digerleri = [y for y in k if not y.ad.startswith(f"g{g}_")]
    assert _cakisma(acik, digerleri) < 1e-3


@pytest.mark.parametrize("dy", [0.0, -100.0, -230.0])
def test_ustune_kayar(dy):
    alt = kutu(1, 2, 1, tavan="evrensel")
    ust = [type(y)(y.ad, y.tur, Pos(0, dy, p.P_Z) * y.parca, y.patlat) for y in kutu(1, 2, 1)]
    tv = [y for y in alt if y.tur in UST + ALT]
    assert _cakisma(tv, ust) < 1e-3
