import pytest
from build123d import Box, Pos, Rot
from kutu import params as p
from kutu.lib import MIN3
from kutu.montaj import kesisim_hacmi, kutu
from kutu.parts.panel import panel

from conftest import hacim


def test_dil_kutu_yuzunden_tasar():
    # dil, nominal kutu yüzünü (y=0) YAN_DIL_H - GAP kadar aşar
    assert panel().bounding_box().min.Y == pytest.approx(p.GAP - p.YAN_DIL_H)


def _oluk_sondasi(z0, z1):
    x0 = p.YAN_KILIT_X - p.YAN_DIL_W / 2
    return Pos(x0, p.GAP, z0) * Box(p.YAN_DIL_W, p.YAN_DIL_H, z1 - z0, align=MIN3)


def test_oluk_kilit_bolgesinden_panel_ustune_kadar_acik():
    z0 = p.T + (p.H - p.KILIT_H) / 2
    assert hacim(panel() & _oluk_sondasi(z0, p.T + p.H + p.DIL)) == pytest.approx(0, abs=1e-6)


def test_tavan_oluk_hizasinda_centikli():
    # montajda güney duvarın oluğu üstündeki tavan bölgesi boş olmalı
    k = kutu(1, 1, 1)
    tavan = next(y for y in k if y.tur == "tavan").parca
    x = p.P_XY / 2 + p.YAN_KILIT_X
    sonda = Pos(x - p.YAN_DIL_W / 2, p.GAP, p.T + p.H) * Box(p.YAN_DIL_W, p.YAN_DIL_H, p.T + p.ERKEK_H, align=MIN3)
    assert hacim(tavan & sonda) == pytest.approx(0, abs=1e-6)


def test_yatay_kiskac_oluk_hizasinda_acik():
    from kutu.parts.yatay_kiskac import yatay_kiskac
    assert hacim(yatay_kiskac() & _oluk_sondasi(p.T + p.H, p.T + p.H + 2 * p.T)) == pytest.approx(0, abs=1e-6)


def _yan_yana(donuk: bool):
    a = kutu(1, 1, 1)
    b = kutu(1, 1, 1)
    c = p.P_XY / 2
    yer = Pos(p.P_XY, 0, 0) * (Pos(c, c, 0) * Rot(0, 0, 180) * Pos(-c, -c, 0) if donuk else Pos(0, 0, 0))
    b = [type(y)(y.ad, y.tur, yer * y.parca, y.patlat) for y in b]
    a_dogu = next(y for y in a if y.ad.endswith("panel_d100"))
    b_bati = next(y for y in b if y.ad.endswith(("panel_b100", "panel_d100")) and
                  y.parca.bounding_box().center().X < p.P_XY + 50)
    return a_dogu.parca, b_bati.parca


@pytest.mark.parametrize("donuk", [False, True])
def test_yan_yana_kutular_cakismadan_kilitlenir(donuk):
    a, b = _yan_yana(donuk)
    assert kesisim_hacmi(a, b) < 1e-3
    # dil karşı oluğa girmiş: iki panel FIT kadar yakın
    assert a.distance_to(b) == pytest.approx(p.FIT, abs=1e-3)


def test_oluk_boydan_boya_acik():
    # 2H kutu, üst üste iki 1H kutunun yanına indirilirken dil hiçbir yerde takılmamalı
    assert hacim(panel() & _oluk_sondasi(p.T - p.DIL, p.T + p.H + p.DIL)) == pytest.approx(0, abs=1e-6)


def test_taban_oluk_hizasinda_centikli():
    k = kutu(1, 1, 1)
    taban = next(y for y in k if y.tur == "taban").parca
    x = p.P_XY / 2 + p.YAN_KILIT_X
    sonda = Pos(x - p.YAN_DIL_W / 2, p.GAP, 0) * Box(p.YAN_DIL_W, p.YAN_DIL_H, p.T, align=MIN3)
    assert hacim(taban & sonda) == pytest.approx(0, abs=1e-6)
