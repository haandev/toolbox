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
    k = kutu(nx, ny, nz, kulp=True, cekmece=True)
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
    k = kutu(1, 1, nz, kulp=True, cekmece=True)
    cekmeceler = [y for y in k if y.tur == "cekmece"]
    digerleri = [y for y in k if y.tur != "cekmece"]
    for c in cekmeceler:
        for dy in (10, 40, 80, p.CEKMECE_YOL - 5):
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


def _cekmece_ve_digerleri(nz=1, kat=0):
    k = kutu(1, 1, nz, kulp=True, cekmece=True)
    c = next(y for y in k if y.ad == f"k{kat}_cekmece_0")
    return c, [y for y in k if y is not c]


def _carpisma(c, digerleri, dy):
    cekilmis = Pos(0, -dy, 0) * c.parca
    return sum(kesisim_hacmi(cekilmis, d.parca) for d in digerleri)


@pytest.mark.parametrize("nz,kat", [(1, 0), (2, 0), (2, 1)])
def test_durdurucu_cekmeceyi_tutar(nz, kat):
    c, digerleri = _cekmece_ve_digerleri(nz, kat)
    assert _carpisma(c, digerleri, p.CEKMECE_YOL - 5) < 1e-3
    assert _carpisma(c, digerleri, p.CEKMECE_YOL + 5) > 1


@pytest.mark.parametrize("nz,kat", [(1, 0), (2, 1)])
def test_kapali_tutucu_hafifce_direnir(nz, kat):
    c, digerleri = _cekmece_ve_digerleri(nz, kat)
    assert _carpisma(c, digerleri, 0) < 1e-3          # kapalı: serbest
    v = _carpisma(c, digerleri, 1.0)                    # 1 mm: tümseğe dayanır
    assert 0.1 < v < 20
    assert _carpisma(c, digerleri, 10) < 1e-3          # tümseği aştıktan sonra serbest


def test_durdurucu_cikintilari_tabanin_dort_kenarinda():
    from build123d import Box
    from kutu.lib import MIN3
    from kutu.parts.karo import karo_taban
    from conftest import hacim
    c = p.P_XY / 2
    w, y0, L = p.DURDURUCU_W, p.DURDURUCU_Y0, p.DURDURUCU_L
    for x0, y0_, sx, sy in ((c - w / 2, y0, w, L), (c - w / 2, p.P_XY - y0 - L, w, L),
                            (y0, c - w / 2, L, w), (p.P_XY - y0 - L, c - w / 2, L, w)):
        sonda = Pos(x0, y0_, p.T) * Box(sx, sy, p.DURDURUCU_H, align=MIN3)
        assert hacim(karo_taban() & sonda) == pytest.approx(sx * sy * p.DURDURUCU_H, rel=1e-3)


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2), (3, 1)])
def test_raf_sehimi_5kg_altinda_1mm(nx, ny):
    from kutu.parts.cekmece import raf_sehimi
    assert raf_sehimi(5.0, nx, ny) < 1.0


def test_kaburgasiz_raf_cok_eger():
    # kaburgaların gerçekten gerekli olduğunu gösterir: aynı hesap düz plaka için
    from kutu.parts.cekmece import raf_sehimi
    assert raf_sehimi(5.0, 1, 1, kaburga=False) > 2.0
