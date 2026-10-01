import itertools

import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.montaj import kesisim_hacmi, kutu


def _sayim(liste):
    s = {}
    for y in liste:
        s[y.tur] = s.get(y.tur, 0) + 1
    return s


def _yan_tasma():
    """Yan kilit dili, gövdenin her iki yanında kutu yüzünü aşar."""
    return 2 * p.RAY_T if p.YAN_KILIT else 0


def _dis_kutu(liste):
    b = liste[0].parca.bounding_box()
    for y in liste[1:]:
        b = b.add(y.parca.bounding_box())
    return b


def _cakisma_yok(liste):
    for a, b in itertools.combinations(liste, 2):
        v = kesisim_hacmi(a.parca, b.parca)
        assert v < 1e-3, f"{a.ad} ile {b.ad} çakışıyor: {v:.3f} mm³"


def test_degen_kutular_sifir():
    a = Box(10, 10, 10, align=MIN3)
    b = Pos(10, 0, 0) * Box(10, 10, 10, align=MIN3)
    assert kesisim_hacmi(a, b) == pytest.approx(0, abs=1e-9)


def test_uzak_kutular_sifir():
    a = Box(10, 10, 10, align=MIN3)
    b = Pos(50, 0, 0) * Box(10, 10, 10, align=MIN3)
    assert kesisim_hacmi(a, b) == 0


def test_cakisan_kutular():
    a = Box(10, 10, 10, align=MIN3)
    b = Pos(5, 0, 0) * Box(10, 10, 10, align=MIN3)
    assert kesisim_hacmi(a, b) == pytest.approx(500)


@pytest.fixture(scope="module")
def k111():
    return kutu(1, 1, 1)


def test_tek_node_sayim(k111):
    assert _sayim(k111) == {"taban": 1, "tavan": 1, "kose": 4, "panel": 4}


def test_tek_node_dis_olcu(k111):
    b = _dis_kutu(k111)
    assert b.size.X == pytest.approx(p.kutu_dis(1, p.P_XY) + _yan_tasma())
    assert b.size.Y == pytest.approx(p.kutu_dis(1, p.P_XY) + _yan_tasma())
    # tavan kılavuz rayları gövdenin KILAVUZ_H üstüne taşar; istifte üstteki tabana girer
    assert b.size.Z == pytest.approx(p.kutu_dis(1, p.P_Z) + p.KILAVUZ_H)
    assert b.min.X == pytest.approx(p.GAP - _yan_tasma() / 2)


def test_tek_node_cakisma_yok(k111):
    _cakisma_yok(k111)


def test_panel_kanalda_fit_boslugu(k111):
    paneller = [y for y in k111 if y.tur == "panel"]
    koseler = [y for y in k111 if y.tur == "kose"]
    karolar = [y for y in k111 if y.tur in ("taban", "tavan")]
    for pnl in paneller:
        en_yakin_kose = min(pnl.parca.distance_to(k.parca) for k in koseler)
        en_yakin_karo = min(pnl.parca.distance_to(k.parca) for k in karolar)
        assert en_yakin_kose == pytest.approx(p.FIT, abs=1e-3)
        assert en_yakin_karo == pytest.approx(p.FIT, abs=1e-3)


def test_kare_olmayan_kutu_2x1():
    k = kutu(2, 1, 1)
    assert _sayim(k) == {"taban": 2, "tavan": 1, "kose": 4, "panel": 6, "kiskac": 2}
    b = _dis_kutu(k)
    assert b.size.X == pytest.approx(p.kutu_dis(2, p.P_XY) + _yan_tasma())
    assert b.size.Y == pytest.approx(p.kutu_dis(1, p.P_XY) + _yan_tasma())
    _cakisma_yok(k)


@pytest.fixture(scope="module")
def k112():
    return kutu(1, 1, 2)


def test_2h_kutu(k112):
    # katlar arası ara raf yok: yatay kıskaç + köşe düğümü
    assert _sayim(k112) == {"taban": 1, "tavan": 1, "kose": 8, "panel": 8, "yatay_kiskac": 4, "kose_dugumu": 4}
    b = _dis_kutu(k112)
    assert b.size.Z == pytest.approx(p.kutu_dis(2, p.P_Z) + p.KILAVUZ_H)
    _cakisma_yok(k112)


def test_2h_paneller_fit_ile_oturur(k112):
    paneller = [y for y in k112 if y.tur == "panel"]
    tutucular = [y for y in k112 if y.tur in ("yatay_kiskac", "kose_dugumu", "taban", "tavan", "kose")]
    for pnl in paneller:
        assert min(pnl.parca.distance_to(t.parca) for t in tutucular) == pytest.approx(p.FIT, abs=1e-3)


def test_2x1x2_kiskac_dugumu():
    k = kutu(2, 1, 2)
    s = _sayim(k)
    assert s["kiskac_dugumu"] == 2 and s["yatay_kiskac"] == 6 and s["kiskac"] == 4
    _cakisma_yok(k)


def test_2x2_sayim_ve_olcu():
    k = kutu(2, 2, 1)
    assert _sayim(k) == {"taban": 4, "tavan": 1, "kose": 4, "panel": 8, "kiskac": 4}
    b = _dis_kutu(k)
    assert b.size.X == pytest.approx(p.kutu_dis(2, p.P_XY) + _yan_tasma())
    assert b.size.Y == pytest.approx(p.kutu_dis(2, p.P_XY) + _yan_tasma())


def test_patlatma_yonleri(k111):
    for y in k111:
        if y.tur in ("taban", "tavan"):
            assert y.patlat[0] == 0 and y.patlat[1] == 0 and y.patlat[2] in (-1, 1)
        else:
            assert y.patlat[2] == 0 and (y.patlat[0], y.patlat[1]) != (0, 0)


def _kaydir(liste, dx, dy, dz):
    return [type(y)(y.ad, y.tur, Pos(dx, dy, dz) * y.parca, y.patlat) for y in liste]


@pytest.mark.parametrize("alt,ust,dx", [((1, 1), (1, 1), 0), ((2, 1), (1, 1), 200)])
def test_istif_erkek_disi_oturur(alt, ust, dx):
    alttaki = kutu(*alt, 1)
    ustteki = _kaydir(kutu(*ust, 1), dx, 0, p.P_Z)
    tavanlar = [y for y in alttaki if y.tur == "tavan"]
    tabanlar = [y for y in ustteki if y.tur == "taban"]
    _cakisma_yok(tavanlar + tabanlar)
    # yanal hizalama boşluğu FIT: erkek bilezik dişi çerçeveye FIT ile oturur
    for tb in tabanlar:
        assert min(tb.parca.distance_to(tv.parca) for tv in tavanlar) == pytest.approx(p.FIT, abs=1e-3)


@pytest.mark.parametrize("dy", [-20.0, -80.0, -150.0, -210.0])
def test_ust_kutu_one_kayarak_cikar(dy):
    alt = kutu(1, 1, 1, kulp=True)
    ust = [type(y)(y.ad, y.tur, Pos(0, dy, p.P_Z) * y.parca, y.patlat) for y in kutu(1, 1, 1)]
    for a in alt:
        if a.tur in ("tavan", "kulp"):
            for b in ust:
                assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad} dy={dy}"
