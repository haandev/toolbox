import math

import pytest
from kutu import params as p
from kutu.lib import kanal, kule, kilit_yeri


def test_yuva_paneli_fit_ile_sarar():
    py0, py1 = kanal.panel_y()
    y0, y1 = kanal.yuva_y()
    assert py1 - py0 == pytest.approx(p.WALL)
    assert py0 - y0 == pytest.approx(p.FIT)
    assert y1 - py1 == pytest.approx(p.FIT)


def test_yuva_kutusu_olculeri():
    b = kanal.yuva(0, 10, 0, 20).bounding_box()
    y0, y1 = kanal.yuva_y()
    assert b.min.Y == pytest.approx(y0)
    assert b.max.Y == pytest.approx(y1)
    assert b.size.X == pytest.approx(10)
    assert b.size.Z == pytest.approx(20)


def test_kule_proto_insert_deligi():
    assert kule.delik_capi() == p.INSERT_DELIK


def test_kule_seri_uretim_deligi(monkeypatch):
    monkeypatch.setattr(p, "PROTO", False)
    assert kule.delik_capi() == pytest.approx(3.2)


def test_kule_geometrisi():
    k = kule.kule(20)
    assert k.is_valid
    b = k.bounding_box()
    assert b.size.X == pytest.approx(p.KULE_OD)
    assert b.min.Z == pytest.approx(0)
    assert b.max.Z == pytest.approx(20)
    dolu = math.pi * (p.KULE_OD / 2) ** 2 * 20
    assert k.volume < dolu


def test_kilit_noktalari_tek_node():
    nk = kilit_yeri.kilit_noktalari(1, 1, 1)
    assert len(nk) == 6
    d = dict(nk)
    assert d["guney"] == (100, 0, 50)
    assert d["kuzey"] == (100, 200, 50)
    assert d["bati"] == (0, 100, 50)
    assert d["dogu"] == (200, 100, 50)
    assert d["alt"] == (100, 100, 0)
    assert d["ust"] == (100, 100, 100)


@pytest.mark.parametrize("nx,ny,nz", [(2, 1, 1), (2, 2, 1), (1, 1, 2), (3, 2, 2)])
def test_kilit_noktalari_sayisi_ve_izgara(nx, ny, nz):
    nk = kilit_yeri.kilit_noktalari(nx, ny, nz)
    assert len(nk) == 2 * (nx + ny) * nz + 2 * nx * ny
    for yuz, (x, y, z) in nk:
        if yuz in ("guney", "kuzey"):
            assert (x - 100) % 200 == 0 and (z - 50) % 100 == 0
        elif yuz in ("bati", "dogu"):
            assert (y - 100) % 200 == 0 and (z - 50) % 100 == 0
        else:
            assert (x - 100) % 200 == 0 and (y - 100) % 200 == 0


def test_panel_bolgesi_merkezde():
    b = kilit_yeri.panel_bolgesi().bounding_box()
    assert b.center().X == pytest.approx(0)
    assert b.center().Z == pytest.approx(p.T + p.H / 2)
    assert b.size.X == pytest.approx(p.KILIT_W)
    assert b.size.Z == pytest.approx(p.KILIT_H)


def test_karo_bolgesi_merkezde():
    b = kilit_yeri.karo_bolgesi().bounding_box()
    assert b.center().X == pytest.approx(p.P_XY / 2)
    assert b.center().Y == pytest.approx(p.P_XY / 2)
    assert b.size.X == pytest.approx(p.KILIT_KARO)
