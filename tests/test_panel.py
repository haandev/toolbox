import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y
from kutu.lib.kilit_yeri import panel_bolgesi
from kutu.parts.panel import panel

from conftest import hacim


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
    assert b.min.Z == pytest.approx(p.T - p.DIL_V)
    # en içteki nokta: kaburgalar ya da tutma girintisinin kabuğu
    assert b.max.Y == pytest.approx(y0 + p.WALL + max(p.RIB_D, p.TUTMA_DERIN + p.WALL))


def test_deri_kalinligi_wall(pnl):
    y0, y1 = panel_y()
    # kilit bölgesinin altında, kaburgasız bir noktada yalnızca deri var
    h = (p.RAY_V1 - p.RAY_H / 2 - p.FIT - p.WALL) - (p.T + 2) - 0.5   # alt ray şeridinin altında
    sonda = Pos(-5, y0 - 1, p.T + 2) * Box(10, p.WALL + p.RIB_D + 2, h, align=MIN3)
    kesit = pnl & sonda
    assert kesit.volume == pytest.approx(10 * h * p.WALL, rel=1e-3)


def test_kilit_bolgesinde_kaburga_yok(monkeypatch):
    # yan kilit kapalıyken kilit bölgesi tamamen boş (kaburga girmez)
    monkeypatch.setattr(p, "YAN_KILIT", False)
    panel.cache_clear()
    try:
        # tutma girintisinin kabuğu hariç
        kabuk = Pos(-p.TUTMA_W / 2 - p.WALL, 0, p.TUTMA_Z0 - p.WALL) * Box(
            p.TUTMA_W + 2 * p.WALL, 50, p.TUTMA_H + 2 * p.WALL, align=MIN3)
        assert hacim(panel() & (panel_bolgesi() - kabuk)) == pytest.approx(0, abs=1e-6)
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
        dil = Pos(p.U / 2, y0, p.T - p.DIL_V) * Box(p.DIL, p.WALL + p.RIB_D, p.PANEL_H, align=MIN3)
        assert (panel() & dil).volume == pytest.approx(p.DIL * p.WALL * p.PANEL_H, rel=1e-3)
    finally:
        panel.cache_clear()


def test_tutma_girintisi_acik_ve_derinin_arkasinda_cep(pnl):
    y0, y1 = panel_y()
    w = p.TUTMA_W / 2 - 1
    acik = Pos(-w, p.GAP, p.TUTMA_Z0 + 0.5) * Box(2 * w, y1 - p.GAP + 0.5, p.TUTMA_ACIK_H - 1, align=MIN3)
    cep = Pos(-w, y1 + 0.2, p.TUTMA_Z0 + 0.5) * Box(2 * w, p.TUTMA_DERIN - 0.4, p.TUTMA_H - 1, align=MIN3)
    tirnak = Pos(-w, y0, p.TUTMA_Z0 + p.TUTMA_ACIK_H + 0.5) * Box(2 * w, p.WALL, p.TUTMA_H - p.TUTMA_ACIK_H - 1, align=MIN3)
    assert hacim(pnl & acik) == pytest.approx(0, abs=1e-6)          # parmak girer
    assert hacim(pnl & cep) == pytest.approx(0, abs=1e-6)           # derinin arkasında boşluk
    assert hacim(pnl & tirnak) == pytest.approx(2 * w * p.WALL * (p.TUTMA_H - p.TUTMA_ACIK_H - 1), rel=1e-3)


def test_tutma_girintisi_raylarin_arasinda():
    alt_serit = p.RAY_V1 + p.RAY_H / 2 + p.FIT + p.WALL
    ust_serit = p.RAY_V2 - p.RAY_H / 2 - p.FIT - p.WALL
    assert alt_serit < p.TUTMA_Z0 - p.WALL
    assert p.TUTMA_Z0 + p.TUTMA_H + p.WALL < ust_serit
