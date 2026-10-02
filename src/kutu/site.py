"""GitHub Pages için statik vitrin: bütün tasarım seçenekleri önceden hesaplanır.

    uv run python -m kutu.site            → site/ (index.html, data/, geo/)

Sunucu yok: her (ölçü, kulp, çekmece, kapak düzeni) için bir JSON; görünüm seçenekleri (kapak açık,
kulp havada) yalnız konumu değişen parçalara ek matris olarak yazılır, çekmeceler tarayıcıda kaydırılır.
"""
import json
import os
import shutil
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path

import numpy as np

from kutu.vitrin import CEKMECE_DISARI, DUZENLER, KOK, Katalog, kapak_duzeni, tasarim

SITE = KOK / "site"
SINIR = {"nx": 4, "ny": 4, "nz": 3}


def site_verisi(katalog: Katalog, nx: int, ny: int, nz: int, kulp: bool, cekmece: bool, duzen: str,
                kopru: bool = True) -> dict:
    taban = tasarim(katalog, nx, ny, nz, kulp, cekmece, duzen, kopru=kopru)
    varyantlar = [(1, 0)] + ([(0, 1), (1, 1)] if kulp else [])
    for ka, kl in varyantlar:
        v = tasarim(katalog, nx, ny, nz, kulp, cekmece, duzen, kapak_acik=bool(ka), kulp_acik=bool(kl),
                    kopru=kopru)
        for o, a in zip(taban["parcalar"], v["parcalar"]):
            assert o["ad"] == a["ad"] and o["geo"] == a["geo"]
            if not np.allclose(o["m"], a["m"], atol=1e-4):
                o.setdefault("v", {})[f"{ka}{kl}"] = a["m"]
    for o in taban["parcalar"]:
        o["m"] = [round(x, 4) for x in o["m"]]
        for k in o.get("v", {}):
            o["v"][k] = [round(x, 4) for x in o["v"][k]]
    taban["cekmece_disari"] = CEKMECE_DISARI
    return taban


def _dosya_adi(nx, ny, nz, kulp, cekmece, kopru, gruplar) -> str:
    g = "-".join(f"{a}{b}{c}{d}" for a, b, c, d in gruplar)
    return f"{nx}{ny}{nz}_{int(kulp)}{int(cekmece)}{int(kopru)}_{g}.json"


def _yaz(is_):
    nx, ny, nz, kulp, cekmece, kopru, duzen = is_
    ad = _dosya_adi(nx, ny, nz, kulp, cekmece, kopru, kapak_duzeni(nx, ny, duzen))
    hedef = SITE / "data" / ad
    if not hedef.exists():
        veri = site_verisi(Katalog(SITE / "geo"), nx, ny, nz, kulp, cekmece, duzen, kopru)
        gecici = hedef.with_suffix(f".{os.getpid()}.tmp")
        gecici.write_text(json.dumps(veri, ensure_ascii=False, separators=(",", ":")))
        os.replace(gecici, hedef)
    return f"{nx},{ny},{nz},{int(kulp)},{int(cekmece)},{int(kopru)},{duzen}", ad


def main() -> None:
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    (SITE / "geo").mkdir(parents=True, exist_ok=True)
    isler = list(product(range(1, SINIR["nx"] + 1), range(1, SINIR["ny"] + 1), range(1, SINIR["nz"] + 1),
                         (False, True), (False, True), (False, True), DUZENLER))
    with ProcessPoolExecutor() as havuz:
        dizin = dict(havuz.map(_yaz, isler, chunksize=4))
    (SITE / "data" / "index.json").write_text(json.dumps({"sinir": SINIR, "dosya": dizin}))
    html = (KOK / "preview" / "vitrin.html").read_text()
    html = html.replace("<script type=\"importmap\">", "<script>window.VITRIN_STATIK = true;</script>\n<script type=\"importmap\">", 1)
    (SITE / "index.html").write_text(html)
    (SITE / ".nojekyll").write_text("")
    print(f"{len(set(dizin.values()))} tasarım, {len(list((SITE / 'geo').glob('*.stl')))} geometri → {SITE}")


if __name__ == "__main__":
    main()
