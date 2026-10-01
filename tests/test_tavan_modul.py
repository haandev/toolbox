"""Tavan modülleri: 1×1, 2×1, 1×2, 2×2 (her biri tek kulplu); büyük kutular bunlarla döşenir."""
import itertools

import pytest
from build123d import Pos
from kutu import params as p
from kutu.montaj import kapak_ac, kesisim_hacmi, kutu
from kutu.parts.tavan import tavan_modulleri


@pytest.mark.parametrize("nx,ny,beklenen", [
    (1, 1, [(0, 0, 1, 1)]),
    (2, 1, [(0, 0, 2, 1)]),
    (2, 2, [(0, 0, 2, 2)]),
    (3, 1, [(0, 0, 2, 1), (2, 0, 1, 1)]),
    (1, 2, [(0, 0, 1, 2)]),
    (3, 2, [(0, 0, 2, 2), (2, 0, 1, 2)]),
    (1, 3, [(0, 0, 1, 2), (0, 2, 1, 1)]),
    (2, 3, [(0, 0, 2, 2), (0, 2, 2, 1)]),
    (4, 2, [(0, 0, 2, 2), (2, 0, 2, 2)]),
])
def test_doseme(nx, ny, beklenen):
    assert sorted(tavan_modulleri(nx, ny)) == sorted(beklenen)


def test_yalniz_uc_modul_tipi():
    tipler = set()
    for nx in range(1, 6):
        for ny in range(1, 5):
            m = tavan_modulleri(nx, ny)
            assert sum(a * b for _, _, a, b in m) == nx * ny          # tam döşeme
            tipler |= {(a, b) for _, _, a, b in m}
    assert tipler == {(1, 1), (2, 1), (1, 2), (2, 2)}


@pytest.mark.parametrize("nx,ny", [(3, 1), (1, 2), (3, 2)])
def test_cok_modullu_kutu_cakismaz(nx, ny):
    k = kutu(nx, ny, 1, kulp=True)
    m = tavan_modulleri(nx, ny)
    say = lambda t: sum(1 for y in k if y.tur == t)
    assert say("cerceve") == len(m) and say("kapak") == len(m) and say("kulp") == len(m)
    assert say("kapak_mandal") == sum(a for _, _, a, _ in m)
    for a, b in itertools.combinations(k, 2):
        assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


@pytest.mark.parametrize("nx,ny,dy", [(3, 1, 0.0), (3, 1, -60.0), (3, 1, -150.0),
                                      (1, 2, 0.0), (1, 2, -100.0), (1, 2, -230.0), (1, 2, -390.0)])
def test_cok_modullu_kutunun_ustune_kayar(nx, ny, dy):
    alt = kutu(nx, ny, 1, kulp=True)
    ust = [type(y)(y.ad, y.tur, Pos(0, dy, p.P_Z) * y.parca, y.patlat) for y in kutu(nx, ny, 1)]
    for a in alt:
        if a.tur in ("kapak", "kapak_mandal", "cerceve", "kulp"):
            for b in ust:
                assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad} dy={dy}"


def test_modul_kapagi_tek_basina_acilir():
    k = kutu(3, 1, 1, kulp=True, kapak_mandal_acik=True)
    grup = [y for y in k if y.ad.startswith("m1_") and y.tur in ("kapak", "kapak_mandal", "kulp")]
    assert grup
    acik = kapak_ac(grup, 1, 1, 90)
    digerleri = [y for y in k if y not in grup]
    for a in acik:
        for b in digerleri:
            assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


def test_4x4_dort_2x2_modul_ve_modul_arasi_kamlar():
    k = kutu(4, 4, 1, kulp=True)
    assert sorted(tavan_modulleri(4, 4)) == [(0, 0, 2, 2), (0, 2, 2, 2), (2, 0, 2, 2), (2, 2, 2, 2)]
    kamlar = [y for y in k if y.tur == "papyon_cerceve"]
    assert len(kamlar) == 2 * (4 + 4)          # x = 400 ve y = 400 ek yerleri, node başına iki kam
    ust = [y for y in k if y.tur in ("cerceve", "kapak", "kapak_mandal", "kulp", "papyon_cerceve")]
    for a, b in itertools.combinations(ust, 2):
        assert kesisim_hacmi(a.parca, b.parca) < 1e-3, f"{a.ad} / {b.ad}"


def test_modul_cerceveleri_kamla_kilitli():
    k = kutu(2, 2, 1)                        # tek 2×2 modül: kam yok
    assert not [y for y in k if y.tur == "papyon_cerceve"]
    k = kutu(3, 1, 1)                        # 2×1 + 1×1
    kamlar = [y for y in k if y.tur == "papyon_cerceve"]
    assert len(kamlar) == 2
    sag = next(y for y in k if y.ad.startswith("m1_cerceve"))
    assert sum(kesisim_hacmi(Pos(1.0, 0, 0) * sag.parca, m.parca) for m in kamlar) > 1
