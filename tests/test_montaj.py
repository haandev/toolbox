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
    assert _sayim(k111) == {"karo": 2, "kose": 4, "panel": 4}


def test_tek_node_dis_olcu(k111):
    b = _dis_kutu(k111)
    assert b.size.X == pytest.approx(p.kutu_dis(1, p.P_XY))
    assert b.size.Y == pytest.approx(p.kutu_dis(1, p.P_XY))
    assert b.size.Z == pytest.approx(p.kutu_dis(1, p.P_Z))
    assert b.min.X == pytest.approx(p.GAP)


def test_tek_node_cakisma_yok(k111):
    _cakisma_yok(k111)


def test_panel_kanalda_fit_boslugu(k111):
    paneller = [y for y in k111 if y.tur == "panel"]
    koseler = [y for y in k111 if y.tur == "kose"]
    karolar = [y for y in k111 if y.tur == "karo"]
    for pnl in paneller:
        en_yakin_kose = min(pnl.parca.distance_to(k.parca) for k in koseler)
        en_yakin_karo = min(pnl.parca.distance_to(k.parca) for k in karolar)
        assert en_yakin_kose == pytest.approx(p.FIT, abs=1e-3)
        assert en_yakin_karo == pytest.approx(p.FIT, abs=1e-3)


def test_kare_olmayan_kutu_2x1():
    k = kutu(2, 1, 1)
    assert _sayim(k) == {"karo": 4, "kose": 4, "panel": 6, "kiskac": 2}
    b = _dis_kutu(k)
    assert b.size.X == pytest.approx(p.kutu_dis(2, p.P_XY))
    assert b.size.Y == pytest.approx(p.kutu_dis(1, p.P_XY))
    _cakisma_yok(k)


def test_2h_kutu():
    k = kutu(1, 1, 2)
    assert _sayim(k) == {"karo": 4, "kose": 8, "panel": 8}
    b = _dis_kutu(k)
    assert b.size.Z == pytest.approx(p.kutu_dis(2, p.P_Z))
    _cakisma_yok(k)


def test_2x2_sayim_ve_olcu():
    k = kutu(2, 2, 1)
    assert _sayim(k) == {"karo": 8, "kose": 4, "panel": 8, "kiskac": 4}
    b = _dis_kutu(k)
    assert b.size.X == pytest.approx(p.kutu_dis(2, p.P_XY))
    assert b.size.Y == pytest.approx(p.kutu_dis(2, p.P_XY))


def test_patlatma_yonleri(k111):
    for y in k111:
        if y.tur == "karo":
            assert y.patlat[0] == 0 and y.patlat[1] == 0 and y.patlat[2] in (-1, 1)
        else:
            assert y.patlat[2] == 0 and (y.patlat[0], y.patlat[1]) != (0, 0)
