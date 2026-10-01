"""Boydan boya T ray: tavanda tam derinlik T raylar, taban karosunda tam boy T kanallar."""
import pytest
from build123d import Box, Pos, Rot
from kutu import params as p
from kutu.lib import MIN3
from kutu.montaj import kesisim_hacmi, kutu
from kutu.parts.karo import karo_taban
from kutu.parts.tavan import tavan

from conftest import TAVAN_TURLERI, hacim

_C = p.P_XY / 2


def _ust(dx=0.0, dy=0.0, dz=0.0, nx=1, ny=1, yer=None):
    yer = yer if yer is not None else Pos(dx, dy, p.P_Z + dz)
    return [type(y)(y.ad, y.tur, yer * y.parca, y.patlat) for y in kutu(nx, ny, 1)]


def _carpisma(alt, ust):
    tv = [y for y in alt if y.tur in TAVAN_TURLERI]
    return sum(kesisim_hacmi(a.parca, b.parca) for a in tv for b in ust)


@pytest.mark.parametrize("ny", [1, 2])
def test_tavanda_boydan_boya_t_raylar(ny):
    t = tavan(1, ny)
    D = ny * p.P_XY
    z = (p.T_BAS_Z0 + p.T_BAS_Z1) / 2
    for hx in (_C - p.T_RAY_X, _C + p.T_RAY_X):
        # kulbun süpürme bölgesi dışında, önden ve arkadan birer uzun bölüm
        # önde: kenardan mafsala kadar; arkada: katlı kulbun arkasından menteşeye kadar
        arka0 = D / 2 + p.KULP_KOL + p.KULP_W / 2 + 3
        arka1 = D - p.GAP - 2 * p.MENTESE_R - 1
        for y0, y1 in ((p.GAP + 1, 40.0), (arka0, arka1)):
            bas = Pos(hx - p.T_BAS_W / 2 + 0.5, y0, z - 0.5) * Box(p.T_BAS_W - 1, y1 - y0, 1, align=MIN3)
            assert hacim(t & bas) == pytest.approx((p.T_BAS_W - 1) * (y1 - y0) * 1, rel=1e-3)


def test_tabanda_iki_yonde_boydan_boya_t_kanal():
    z_boyun = (p.GAP + p.T_BOYUN_Z1) / 2
    z_bas = (p.T_BOYUN_Z1 + p.T_KANAL_Z1) / 2
    for hx in (_C - p.T_RAY_X, _C + p.T_RAY_X):
        boyun = Pos(hx - p.T_BOYUN_W / 2, 0, z_boyun - 0.3) * Box(p.T_BOYUN_W, p.P_XY, 0.6, align=MIN3)
        bas = Pos(hx - p.T_BAS_W / 2, 0, z_bas - 0.3) * Box(p.T_BAS_W, p.P_XY, 0.6, align=MIN3)
        assert hacim(karo_taban() & boyun) == pytest.approx(0, abs=1e-6)
        assert hacim(karo_taban() & bas) == pytest.approx(0, abs=1e-6)
        yan = Pos(0, hx - p.T_BAS_W / 2, z_bas - 0.3) * Box(p.P_XY, p.T_BAS_W, 0.6, align=MIN3)
        assert hacim(karo_taban() & yan) == pytest.approx(0, abs=1e-6)
        # tutma çıkıntısı çerçevede ve cepte var
        for y in (10.0, 50.0):
            cik = Pos(hx + p.T_BOYUN_W / 2 + p.FIT + 0.2, y, p.GAP) * Box(1, 5, p.T_BOYUN_Z1 - p.GAP - 0.1, align=MIN3)
            assert hacim(karo_taban() & cik) > 0


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2)])
def test_istifte_cakismaz(nx, ny):
    assert _carpisma(kutu(nx, ny, 1, kulp=True), _ust(nx=nx, ny=ny)) < 1e-3


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1)])
def test_dikey_kilit(nx, ny):
    assert _carpisma(kutu(nx, ny, 1, kulp=True), _ust(dz=1.0, nx=nx, ny=ny)) > 1


@pytest.mark.parametrize("dx", [-1.0, 1.0])
def test_yanda_hizalar(dx):
    assert _carpisma(kutu(1, 1, 1, kulp=True), _ust(dx=dx)) > 1


@pytest.mark.parametrize("dy", [-3.0, -40.0, -100.0, -170.0, -205.0])
def test_one_kayarak_cikar_ve_takilir(dy):
    assert _carpisma(kutu(1, 1, 1, kulp=True), _ust(dy=dy)) < 1e-3


@pytest.mark.parametrize("dy", [-40.0, -150.0, -250.0, -390.0])
def test_iki_derin_kutuda_kayar(dy):
    assert _carpisma(kutu(1, 2, 1, kulp=True), _ust(dy=dy, ny=2)) < 1e-3


@pytest.mark.parametrize("aci", [90, 180])
def test_dondurulmus_ust_kutu_da_kilitlenir(aci):
    yer = Pos(0, 0, p.P_Z) * Pos(_C, _C, 0) * Rot(0, 0, aci) * Pos(-_C, -_C, 0)
    alt = kutu(1, 1, 1, kulp=True)
    assert _carpisma(alt, _ust(yer=yer)) < 1e-3
    assert _carpisma(alt, _ust(yer=Pos(0, 0, 1) * yer)) > 1


def test_node_kapasitesi_en_az_1000N():
    from kutu.parts.t_kanal import node_kapasitesi
    assert node_kapasitesi(1, 1) >= 1000.0


def test_kanal_panel_olugunun_altinda():
    assert p.T_KANAL_Z1 < p.T - p.DIL_V - p.FIT
