"""Hata önleyici anahtar: panel yalnızca doğru yönde takılabilir."""
import pytest
from build123d import Box, Pos, Rot
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y
from kutu.montaj import kesisim_hacmi, kutu
from kutu.parts.panel import panel
from kutu.parts.yatay_kiskac import yatay_kiskac

from conftest import OLUK_TURLERI, TAVAN_TURLERI, hacim


def _anahtar_sondasi(z0, z1):
    _, y_ic = panel_y()
    return Pos(p.ANAHTAR_X - p.ANAHTAR_W / 2, y_ic, z0) * Box(p.ANAHTAR_W, p.ANAHTAR_T, z1 - z0, align=MIN3)


def test_anahtar_yalniz_alt_dilde():
    alt = _anahtar_sondasi(p.T - p.DIL_V, p.T)
    ust = _anahtar_sondasi(p.T + p.H, p.T + p.H + p.DIL_V)
    assert hacim(panel() & alt) == pytest.approx(p.ANAHTAR_W * p.ANAHTAR_T * p.DIL_V, rel=1e-3)
    assert hacim(panel() & ust) == pytest.approx(0, abs=1e-6)


def test_yatay_kiskac_ust_olukta_cep_alt_olukta_yok():
    z0 = p.T + p.H
    ust_cep = _anahtar_sondasi(z0 + 2 * p.T - p.DIL_V, z0 + 2 * p.T)
    alt = _anahtar_sondasi(z0, z0 + p.DIL_V)
    assert hacim(yatay_kiskac() & ust_cep) == pytest.approx(0, abs=1e-6)
    assert hacim(yatay_kiskac() & alt) > 0


def _guney_paneli_degistir(donusum):
    k = kutu(1, 1, 1)
    guney = next(y for y in k if y.ad.endswith("panel_g100"))
    c = Pos(p.P_XY / 2, 0, p.P_Z / 2)
    yanlis = c * donusum * Pos(-p.P_XY / 2, 0, -p.P_Z / 2) * guney.parca
    digerleri = [y for y in k if y.tur in ("taban",) + OLUK_TURLERI]
    return yanlis, digerleri


def test_dogru_takilan_panel_cakismaz():
    yanlis, digerleri = _guney_paneli_degistir(Rot(0, 0, 0))
    assert sum(kesisim_hacmi(yanlis, d.parca) for d in digerleri) < 1e-3


def test_bas_asagi_takilan_panel_tavana_carpar():
    yanlis, digerleri = _guney_paneli_degistir(Rot(0, 180, 0))   # yüz normali etrafında 180°
    assert sum(kesisim_hacmi(yanlis, d.parca) for d in digerleri) > 1


def test_ici_disina_takilan_panel_tabana_carpar():
    # dikey eksen etrafında 180°, deri aynı kanal düzleminde kalacak şekilde aynalanmış konum
    k = kutu(1, 1, 1)
    guney = next(y for y in k if y.ad.endswith("panel_g100"))
    y0, y1 = panel_y()
    ym = (y0 + y1) / 2
    yanlis = Pos(p.P_XY / 2, ym, 0) * Rot(0, 0, 180) * Pos(-p.P_XY / 2, -ym, 0) * guney.parca
    tabanlar = [y for y in k if y.tur == "taban"]
    assert sum(kesisim_hacmi(yanlis, d.parca) for d in tabanlar) > 1


def test_bati_paneli_montajdaki_bas_asagi_haliyle_cakismaz():
    k = kutu(1, 1, 1)
    bati = next(y for y in k if y.ad.endswith("panel_b100"))
    digerleri = [y for y in k if y.tur in ("taban",) + OLUK_TURLERI]
    assert sum(kesisim_hacmi(bati.parca, d.parca) for d in digerleri) < 1e-3


def test_dogu_paneli_bas_asagi_takilirsa_tavana_carpar():
    k = kutu(1, 1, 1)
    dogu = next(y for y in k if y.ad.endswith("panel_d100"))
    c = Pos(p.P_XY, p.P_XY / 2, p.P_Z / 2)
    # duvar düzleminde (x = sabit) dikey eksen değil, yüz normali (x) etrafında 180°
    yanlis = c * Rot(180, 0, 0) * Pos(-p.P_XY, -p.P_XY / 2, -p.P_Z / 2) * dogu.parca
    tavan = [y for y in k if y.tur in OLUK_TURLERI]
    assert sum(kesisim_hacmi(yanlis, t.parca) for t in tavan) > 1
