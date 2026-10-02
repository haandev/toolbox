import numpy as np
import pytest

from kutu import params as p
from kutu.montaj import kutu
from kutu.vitrin import CEKMECE_DISARI, Katalog, kapak_duzeni, tasarim


def test_bloklar_duzeni_yalniz_kulplu_grup_boylari():
    for nx in range(1, 6):
        for ny in range(1, 6):
            g = kapak_duzeni(nx, ny, "bloklar")
            assert {(gx, gy) for _, _, gx, gy in g} <= {(1, 1), (2, 1), (2, 2)}
            hucre = [(i, j) for i0, j0, gx, gy in g for i in range(i0, i0 + gx) for j in range(j0, j0 + gy)]
            assert len(hucre) == len(set(hucre)) == nx * ny


def test_tek_ve_node_duzenleri():
    assert kapak_duzeni(3, 2, "tek") == [(0, 0, 3, 2)]
    assert len(kapak_duzeni(3, 2, "node")) == 6


def test_tasarim_parca_sayisi_montajla_ayni(tmp_path):
    k = Katalog(tmp_path)
    t = tasarim(k, 2, 2, 1, kulp=True, cekmece=False, duzen="bloklar")
    assert len(t["parcalar"]) == len(kutu(2, 2, 1, kulp=True, kapak_gruplari=[(0, 0, 2, 2)]))
    assert sum(r["adet"] for r in t["liste"]) == len(t["parcalar"])


def test_cekmece_on_paneli_yerine_cekmece(tmp_path):
    k = Katalog(tmp_path)
    duvar = {r["tur"]: r["adet"] for r in tasarim(k, 2, 1, 1, False, False, "tek")["liste"]}
    cek = {r["tur"]: r["adet"] for r in tasarim(k, 2, 1, 1, False, True, "tek")["liste"]}
    assert cek["cekmece"] == 2 and "cekmece" not in duvar
    assert duvar["panel"] - cek["panel"] == 2


def test_ornek_donusumu_parcayi_yerine_koyar(tmp_path):
    """Örnek = matris × katalog geometrisi; sınır kutusu montajdaki parçayla aynı."""
    k = Katalog(tmp_path)
    t = tasarim(k, 2, 1, 1, kulp=True, cekmece=True, duzen="tek")
    liste = kutu(2, 1, 1, kulp=True, cekmece=True, kapak_gruplari=[(0, 0, 2, 1)])
    for o, y in zip(t["parcalar"], liste):
        ref = k.sekil(o["geo"])
        bb = ref.bounding_box()
        kose = np.array([[x, yy, z, 1] for x in (bb.min.X, bb.max.X) for yy in (bb.min.Y, bb.max.Y)
                         for z in (bb.min.Z, bb.max.Z)])
        M = np.array(o["m"]).reshape(4, 4)
        q = (M @ kose.T).T[:, :3]
        hb = y.parca.bounding_box()
        assert q.min(0) == pytest.approx([hb.min.X, hb.min.Y, hb.min.Z], abs=0.5), y.ad
        assert q.max(0) == pytest.approx([hb.max.X, hb.max.Y, hb.max.Z], abs=0.5), y.ad
    assert (tmp_path / f"{t['parcalar'][0]['geo']}.stl").exists()


def test_katalog_ortak_geometriyi_bir_kez_yazar(tmp_path):
    k = Katalog(tmp_path)
    t = tasarim(k, 3, 2, 1, False, False, "tek")
    assert len({o["geo"] for o in t["parcalar"]}) < 20
    sayi = len(list(tmp_path.glob("*.stl")))
    tasarim(k, 3, 2, 1, False, False, "tek")
    assert len(list(tmp_path.glob("*.stl"))) == sayi


def test_hazir_malzeme_boyla_listelenir(tmp_path):
    k = Katalog(tmp_path)
    liste = tasarim(k, 2, 1, 1, kulp=True, cekmece=False, duzen="tek")["liste"]
    cubuk = next(r for r in liste if r["tur"] == "kulp_cubugu")
    assert cubuk["hazir"] and f"{2 * p.P_XY - 2 * p.KULP_AYAK_U:g}" in cubuk["olcu"]


def _bb(t, ad):
    o = next(o for o in t["parcalar"] if o["ad"] == ad)
    return np.array(o["m"]).reshape(4, 4)


def test_gorunum_kapak_acik_kapak_parcalarini_dondurur(tmp_path):
    k = Katalog(tmp_path)
    kapali = tasarim(k, 1, 1, 1, True, False, "tek")
    acik = tasarim(k, 1, 1, 1, True, False, "tek", kapak_acik=True)
    assert not np.allclose(_bb(kapali, "g0_kapak_hucre_00"), _bb(acik, "g0_kapak_hucre_00"))
    assert np.allclose(_bb(kapali, "cerceve_kenari_00_g"), _bb(acik, "cerceve_kenari_00_g"))


def test_gorunum_kulp_havada_ve_cekmece_disarida(tmp_path):
    k = Katalog(tmp_path)
    a = tasarim(k, 1, 1, 1, True, True, "tek")
    b = tasarim(k, 1, 1, 1, True, True, "tek", kulp_acik=True, cekmece_disari=True)
    assert not np.allclose(_bb(a, "g0_kulp_cubugu"), _bb(b, "g0_kulp_cubugu"))
    dy = _bb(b, "k0_cekmece_0")[1, 3] - _bb(a, "k0_cekmece_0")[1, 3]
    assert dy == pytest.approx(-CEKMECE_DISARI)


def test_ayna_ikiz_kollar_tek_satir(tmp_path):
    liste = tasarim(Katalog(tmp_path), 1, 1, 1, True, False, "tek")["liste"]
    assert [r["adet"] for r in liste if r["tur"] == "kulp_kolu"] == [4]


def test_site_verisi_gorunum_varyantlari(tmp_path):
    from kutu.site import site_verisi
    k = Katalog(tmp_path)
    v = site_verisi(k, 1, 1, 1, True, True, "tek")
    acik = tasarim(k, 1, 1, 1, True, True, "tek", kapak_acik=True, kulp_acik=True)
    for o, a in zip(v["parcalar"], acik["parcalar"]):
        assert np.allclose(o.get("v", {}).get("11", o["m"]), a["m"], atol=1e-3), o["ad"]
    assert "v" not in next(o for o in v["parcalar"] if o["tur"] == "taban")
    assert v["cekmece_disari"] == pytest.approx(CEKMECE_DISARI)


def test_kopru_secenegi_parca_listesine_yansir(tmp_path):
    k = Katalog(tmp_path)
    say = lambda t: sum(r["adet"] for r in t["liste"] if r["tur"].startswith("cerceve_kenari"))
    assert say(tasarim(k, 2, 2, 1, False, False, "tek")) == 16
    assert say(tasarim(k, 2, 2, 1, False, False, "tek", kopru=False)) == 8
