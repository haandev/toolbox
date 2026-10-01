import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.parts.karo import karo_taban, karo_tavan

from conftest import hacim

_IC = p.P_XY - 2 * p.K          # tabanın çerçeve içi (dişi yuva) ölçüsü


def test_tavan_erkek_bilezik_tasar():
    b = karo_tavan().bounding_box()
    assert karo_tavan().is_valid
    # yerel çerçevede kilit yüzü z = GAP; bilezik ERKEK_H kadar taşar
    assert b.min.Z == pytest.approx(p.GAP - p.ERKEK_H)
    assert b.max.Z == pytest.approx(p.T)


def test_tavan_bilezik_dis_olcusu():
    alt = Pos(0, 0, p.GAP - p.ERKEK_H) * Box(p.P_XY, p.P_XY, p.ERKEK_H, align=MIN3)
    bilezik = karo_tavan() & alt
    b = bilezik.bounding_box()
    assert b.size.X == pytest.approx(_IC - 2 * p.FIT)
    assert b.size.Y == pytest.approx(_IC - 2 * p.FIT)
    # içi boş: dolu kare değil
    assert bilezik.volume < 0.2 * b.size.X * b.size.Y * p.ERKEK_H


def test_taban_kaburgalari_bilezik_bandinda_kisa():
    bant = p.WALL + 2 * p.FIT
    derin = p.ERKEK_H + p.FIT
    sonda = Pos(p.K, p.K, p.GAP) * Box(_IC, bant, derin, align=MIN3)
    assert hacim(karo_taban() & sonda) == pytest.approx(0, abs=1e-6)


def test_taban_kilit_yuzunden_tasmaz():
    assert karo_taban().bounding_box().min.Z == pytest.approx(p.GAP)
