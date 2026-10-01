import pytest
from kutu import params as p
from kutu.lib import yan_ray


def test_ray_yukseklikleri_simetrik():
    assert p.RAY_V1 + p.RAY_V2 == pytest.approx(2 * (p.T + p.H / 2))
    assert p.RAY_V1 < p.RAY_V2


def test_dil_kesiti():
    b = yan_ray.dil(-10, 10).bounding_box()
    assert b.size.Z == pytest.approx(p.RAY_H)
    assert b.min.Y == pytest.approx(p.GAP - p.RAY_T)
    assert b.center().Z == pytest.approx(p.RAY_V1)


def test_oluk_komsu_dili_fit_ile_sarar():
    b = yan_ray.oluk(-10, 10, p.RAY_V2).bounding_box()
    assert b.size.Z == pytest.approx(p.RAY_H + 2 * p.FIT)
    # komşunun dil ucu: komşu yüzü y = -GAP'te, dil RAY_T taşar → y = RAY_T - GAP
    assert b.max.Y == pytest.approx(p.RAY_T - p.GAP + p.FIT)


def test_dis_oluklar_iki_yukseklikte():
    o = yan_ray.dis_oluklar(-10, 10)
    zs = sorted(round(s.bounding_box().center().Z, 3) for s in o.solids())
    assert zs == [pytest.approx(p.RAY_V1), pytest.approx(p.RAY_V2)]
