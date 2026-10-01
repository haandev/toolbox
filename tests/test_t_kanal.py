"""T kanal: tavandaki sabit T kancalar, üst taban karosundaki önü açık T kanallara girer."""
import itertools

import pytest
from build123d import Box, Pos, Rot
from kutu import params as p
from kutu.lib import MIN3
from kutu.montaj import kesisim_hacmi, kutu
from kutu.parts.karo import karo_taban
from kutu.parts.tavan import tavan

from conftest import hacim


def _ust(dx=0.0, dy=0.0, dz=0.0, nx=1, ny=1, yer=None):
    yer = yer if yer is not None else Pos(dx, dy, p.P_Z + dz)
    return [type(y)(y.ad, y.tur, yer * y.parca, y.patlat) for y in kutu(nx, ny, 1)]


def _carpisma(alt, ust):
    tv = [y for y in alt if y.tur in ("tavan", "kulp")]
    return sum(kesisim_hacmi(a.parca, b.parca) for a in tv for b in ust)


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2)])
def test_tavanda_on_ve_arka_kanca(nx, ny):
    t = tavan(nx, ny)
    c = p.P_XY / 2
    D = ny * p.P_XY
    for i in range(nx):
        for x, y in ((i * p.P_XY + c + p.T_KANCA_X, 10.0), (i * p.P_XY + c - p.T_KANCA_X, D - 10.0)):
            bas = Pos(x, y, (p.T_BAS_Z0 + p.T_BAS_Z1) / 2) * Box(2 * p.T_BAS_W / 2 - 1, 4, 0.5)
            assert hacim(t & bas) > 0


def test_tabanda_t_kanal_ve_gecit_bos():
    c = p.P_XY / 2
    hx = c + p.T_KANCA_X
    # T kanal: boyun ve baş bölgesi boş, boyun yanlarında tutma çıkıntısı var
    boyun = Pos(hx - p.T_BOYUN_W / 2, p.GAP, p.GAP) * Box(p.T_BOYUN_W, p.K - p.GAP, p.T_BOYUN_Z1 - p.GAP, align=MIN3)
    bas = Pos(hx - p.T_BAS_W / 2, p.GAP, p.T_BOYUN_Z1) * Box(p.T_BAS_W, p.K - p.GAP, p.T_BAS_Z1 - p.T_BOYUN_Z1, align=MIN3)
    cikinti = Pos(hx + p.T_BOYUN_W / 2 + p.FIT + 0.1, p.GAP, p.GAP) * Box(1, p.K - p.GAP, p.T_BOYUN_Z1 - p.GAP - 0.1, align=MIN3)
    assert hacim(karo_taban() & boyun) == pytest.approx(0, abs=1e-6)
    assert hacim(karo_taban() & bas) == pytest.approx(0, abs=1e-6)
    assert hacim(karo_taban() & cikinti) > 0
    # karşı kenarın kancası için düz geçit (+x tarafı)
    gx = c - p.T_KANCA_X
    gecit = Pos(gx - p.T_BAS_W / 2, p.GAP, p.GAP) * Box(p.T_BAS_W, p.K - p.GAP, p.T_BAS_Z1 - p.GAP, align=MIN3)
    assert hacim(karo_taban() & gecit) == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1), (2, 2)])
def test_istifte_cakismaz(nx, ny):
    alt = kutu(nx, ny, 1, kulp=True)
    assert _carpisma(alt, _ust(nx=nx, ny=ny)) < 1e-3


@pytest.mark.parametrize("nx,ny", [(1, 1), (2, 1)])
def test_dikey_kilit(nx, ny):
    alt = kutu(nx, ny, 1, kulp=True)
    assert _carpisma(alt, _ust(dz=1.0, nx=nx, ny=ny)) > 1


@pytest.mark.parametrize("dy", [-3.0, -10.0, -40.0, -100.0, -170.0, -190.0, -205.0])
def test_one_kayarak_cikar_ve_takilir(dy):
    alt = kutu(1, 1, 1, kulp=True)
    assert _carpisma(alt, _ust(dy=dy)) < 1e-3


@pytest.mark.parametrize("dy", [-40.0, -150.0, -250.0, -390.0])
def test_iki_derin_kutuda_kayar(dy):
    alt = kutu(1, 2, 1, kulp=True)
    assert _carpisma(alt, _ust(dy=dy, ny=2)) < 1e-3


@pytest.mark.parametrize("aci", [90, 180])
def test_dondurulmus_ust_kutu_da_kilitlenir(aci):
    c = p.P_XY / 2
    yer = Pos(0, 0, p.P_Z) * Pos(c, c, 0) * Rot(0, 0, aci) * Pos(-c, -c, 0)
    alt = kutu(1, 1, 1, kulp=True)
    assert _carpisma(alt, _ust(yer=yer)) < 1e-3
    assert _carpisma(alt, _ust(yer=Pos(0, 0, 1) * yer)) > 1
