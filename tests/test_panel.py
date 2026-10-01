import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y
from kutu.lib.kilit_yeri import panel_bolgesi
from kutu.parts.panel import panel


@pytest.fixture(scope="module")
def pnl():
    return panel()


def test_gecerli_kati(pnl):
    assert pnl.is_valid


def test_dis_olculer(pnl):
    b = pnl.bounding_box()
    y0, _ = panel_y()
    assert b.size.X == pytest.approx(p.PANEL_L)
    assert b.size.Z == pytest.approx(p.PANEL_H)
    assert b.min.Z == pytest.approx(p.T - p.DIL)
    assert b.max.Y == pytest.approx(y0 + p.WALL + p.RIB_D)


def test_deri_kalinligi_wall(pnl):
    y0, y1 = panel_y()
    # kilit bölgesinin altında, kaburgasız bir noktada yalnızca deri var
    sonda = Pos(-5, y0 - 1, p.T + 2) * Box(10, p.WALL + p.RIB_D + 2, 10, align=MIN3)
    kesit = pnl & sonda
    assert kesit.volume == pytest.approx(10 * 10 * p.WALL, rel=1e-3)


def test_kilit_bolgesinde_kaburga_yok(monkeypatch):
    # yan kilit kapalıyken kilit bölgesi tamamen boş (kaburga girmez)
    monkeypatch.setattr(p, "YAN_KILIT", False)
    panel.cache_clear()
    try:
        assert (panel() & panel_bolgesi()).volume == pytest.approx(0, abs=1e-6)
    finally:
        panel.cache_clear()


def test_yan_kilit_kapaliyken_kutu_yuzunu_asmaz(monkeypatch):
    monkeypatch.setattr(p, "YAN_KILIT", False)
    panel.cache_clear()
    try:
        assert panel().bounding_box().min.Y == pytest.approx(p.GAP + p.LIP)
    finally:
        panel.cache_clear()


def test_kaburgalar_kanala_girmez(monkeypatch):
    # dil bölgesinde (|x| > U/2) yalnızca deri bulunur (yan ray oluğu hariç tutulur)
    monkeypatch.setattr(p, "YAN_KILIT", False)
    panel.cache_clear()
    try:
        y0, _ = panel_y()
        dil = Pos(p.U / 2, y0, p.T - p.DIL) * Box(p.DIL, p.WALL + p.RIB_D, p.PANEL_H, align=MIN3)
        assert (panel() & dil).volume == pytest.approx(p.DIL * p.WALL * p.PANEL_H, rel=1e-3)
    finally:
        panel.cache_clear()
