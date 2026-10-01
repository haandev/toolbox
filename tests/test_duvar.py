"""Kayar duvar: kutulardan kurulan duvarda herhangi bir kutu öne kayarak çıkar, üstteki düşmez."""
import itertools

import pytest
from build123d import Pos
from kutu import params as p
from kutu.montaj import kesisim_hacmi, kutu


def _yerlestir(liste, x, y, z, on_ek):
    return [type(e)(f"{on_ek}/{e.ad}", e.tur, Pos(x, y, z) * e.parca, e.patlat) for e in liste]


def duvar(sutun: int, kat: int, ozel=None):
    """1×1 kutulardan duvar; ozel[(i, k)] = kutu listesi ile tek tek değiştirilebilir."""
    kutular = {}
    for i in range(sutun):
        for k in range(kat):
            liste = (ozel or {}).get((i, k)) or kutu(1, 1, 1, kulp=True)
            kutular[(i, k)] = _yerlestir(liste, i * p.P_XY, 0, k * p.P_Z, f"{i}{k}")
    return kutular


def _cakisma(a, b):
    return sum(kesisim_hacmi(x.parca, y.parca) for x in a for y in b)


def _kutular_arasi_cakisma_yok(kutular):
    for (ka, a), (kb, b) in itertools.combinations(kutular.items(), 2):
        assert _cakisma(a, b) < 1e-3, f"{ka} / {kb}"


@pytest.mark.parametrize("sutun,kat", [(2, 2), (3, 2)])
def test_duvar_cakismaz(sutun, kat):
    _kutular_arasi_cakisma_yok(duvar(sutun, kat))


@pytest.mark.parametrize("dy", [-5.0, -40.0, -100.0, -160.0, -205.0])
def test_alt_orta_kutu_one_kayarak_cikar(dy):
    d = duvar(3, 2)
    cekilen = [type(e)(e.ad, e.tur, Pos(0, dy, 0) * e.parca, e.patlat) for e in d.pop((1, 0))]
    for anahtar, diger in d.items():
        assert _cakisma(cekilen, diger) < 1e-3, f"{anahtar} dy={dy}"


def test_alt_kutu_cikinca_ustteki_komsu_raylarinda_asili():
    d = duvar(3, 2)
    d.pop((1, 0))                                     # alt orta kutu çıkarıldı
    ust = d.pop((1, 1))
    asagi = [type(e)(e.ad, e.tur, Pos(0, 0, -1.0) * e.parca, e.patlat) for e in ust]
    komsular = d[(0, 1)] + d[(2, 1)]
    assert _cakisma(asagi, komsular) > 1             # 1 mm bile inemez: yan raylara dayanır


def test_kenar_sutunda_tek_komsu_da_tasir():
    d = duvar(2, 2)
    d.pop((0, 0))
    ust = d.pop((0, 1))
    asagi = [type(e)(e.ad, e.tur, Pos(0, 0, -1.0) * e.parca, e.patlat) for e in ust]
    assert _cakisma(asagi, d[(1, 1)]) > 1


def test_2h_kutu_yaninda_iki_1h_kutu():
    kutular = {"2h": _yerlestir(kutu(1, 1, 2, kulp=True), 0, 0, 0, "2h"),
               "alt": _yerlestir(kutu(1, 1, 1, kulp=True), p.P_XY, 0, 0, "alt"),
               "ust": _yerlestir(kutu(1, 1, 1, kulp=True), p.P_XY, 0, p.P_Z, "ust")}
    _kutular_arasi_cakisma_yok(kutular)
    cekilen = [type(e)(e.ad, e.tur, Pos(0, -120, 0) * e.parca, e.patlat) for e in kutular["alt"]]
    assert _cakisma(cekilen, kutular["2h"] + kutular["ust"]) < 1e-3


def test_cekmeceli_kutu_duvarda():
    d = duvar(3, 2, ozel={(1, 0): kutu(1, 1, 1, kulp=True, cekmece=True)})
    _kutular_arasi_cakisma_yok(d)


def test_karma_istif_cakismaz():
    from kutu.export import karma_gruplar
    kutular = {a: [type(e)(f"{a}/{e.ad}", e.tur, yer * e.parca, e.patlat) for e in liste]
               for a, liste, yer in karma_gruplar()}
    _kutular_arasi_cakisma_yok(kutular)
