import json

from kutu.montaj import kutu

from kutu.export import disa_aktar


def test_disa_aktar_tek_node(tmp_path):
    m = disa_aktar(tmp_path, 1, 1, 1)
    for tur in ("panel", "kose", "kiskac", "taban", "cerceve", "kapak", "kapak_mandal", "kulp_2x"):
        assert (tmp_path / "step" / f"{tur}.step").stat().st_size > 0
        assert (tmp_path / "stl" / f"{tur}.stl").stat().st_size > 0
    disk = json.loads((tmp_path / "preview" / "manifest.json").read_text())
    assert disk == m
    assert m["kutu"] == {"nx": 1, "ny": 1, "nz": 1, "P_XY": 200, "P_Z": 100}
    assert len(m["parcalar"]) == len(kutu(1, 1, 1, kulp=True))
    assert len(m["kilit"]) == 6
    for parca in m["parcalar"]:
        assert (tmp_path / "preview" / parca["dosya"]).stat().st_size > 0
        assert parca["renk"].startswith("#")
        assert len(parca["patlat"]) == 3


def test_yeniden_aktarma_eski_onizlemeyi_temizler(tmp_path):
    disa_aktar(tmp_path, 2, 1, 1)
    disa_aktar(tmp_path, 1, 1, 1)
    stl = list((tmp_path / "preview").glob("*.stl"))
    assert len(stl) == len(kutu(1, 1, 1, kulp=True))


def test_istif_aktar(tmp_path):
    from kutu.export import istif_aktar
    m = istif_aktar(tmp_path)
    assert len(m["parcalar"]) == len(kutu(2, 1, 1, kulp=True)) + len(kutu(1, 1, 1, kulp=True))
    assert all((tmp_path / "istif" / x["dosya"]).stat().st_size > 0 for x in m["parcalar"])


def test_yan_yana_aktar(tmp_path):
    from kutu.export import yan_yana_aktar
    m = yan_yana_aktar(tmp_path)
    assert len(m["parcalar"]) == 2 * len(kutu(1, 1, 1)) + len(kutu(1, 1, 2))


def test_duvar_sahnesi(tmp_path):
    from kutu.export import duvar_sahnesi_aktar
    m = duvar_sahnesi_aktar(tmp_path)
    assert len(m["parcalar"]) == 6 * len(kutu(1, 1, 1, kulp=True))
