"""Çekmece: ön yüzde panel yerine çekmece; 2H ve üstünde kat arası raf."""
import itertools

import pytest
from build123d import Pos
from kutu import params as p
from kutu.lib.kanal import panel_y
from kutu.montaj import kesisim_hacmi, kutu


def _sayim(liste):
    s = {}
    for y in liste:
        s[y.tur] = s.get(y.tur, 0) + 1
    return s


def _cakisma_yok(liste):
    for a, b in itertools.combinations(liste, 2):
        assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


@pytest.mark.parametrize("nx,ny,nz", [(1, 1, 1), (2, 1, 1), (1, 1, 2), (2, 1, 2)])
def test_cekmeceli_kutu_cakismaz(nx, ny, nz):
    k = kutu(nx, ny, nz, kulp=True, mandal=True, cekmece=True)
    s = _sayim(k)
    assert s["cekmece"] == nx * nz
    assert s["panel"] == (nx + 2 * ny) * nz          # ön yüzde panel yok
    assert s.get("raf", 0) == nz - 1
    _cakisma_yok(k)


def test_on_yuz_panelle_ayni_hizada():
    k = kutu(1, 1, 1, cekmece=True)
    c = next(y for y in k if y.tur == "cekmece")
    y0, _ = panel_y()
    assert c.parca.bounding_box().min.Y == pytest.approx(y0)


@pytest.mark.parametrize("nz", [1, 2])
def test_cekmece_disari_cekilebilir(nz):
    k = kutu(1, 1, nz, kulp=True, mandal=True, cekmece=True)
    cekmeceler = [y for y in k if y.tur == "cekmece"]
    digerleri = [y for y in k if y.tur != "cekmece"]
    for c in cekmeceler:
        for dy in (10, 40, 80, 120, 180):
            cekilmis = Pos(0, -dy, 0) * c.parca
            for d in digerleri:
                assert kesisim_hacmi(cekilmis, d.parca) < 1e-3, f"{c.ad} -{dy} / {d.ad}"


def test_ust_cekmece_rafa_fit_ile_oturur():
    k = kutu(1, 1, 2, cekmece=True)
    raf = next(y for y in k if y.tur == "raf")
    ust = max((y for y in k if y.tur == "cekmece"), key=lambda y: y.parca.bounding_box().min.Z)
    assert ust.parca.distance_to(raf.parca) == pytest.approx(p.FIT, abs=1e-3)


def test_raf_yatay_kiskaclara_oturur():
    k = kutu(1, 1, 2, cekmece=True)
    raf = next(y for y in k if y.tur == "raf")
    yataylar = [y for y in k if y.tur == "yatay_kiskac"]
    assert min(raf.parca.distance_to(y.parca) for y in yataylar) == pytest.approx(0, abs=1e-6)
