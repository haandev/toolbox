"""Vitrin: tarayıcıda kutu tasarlama ve istif önizleme sunucusu.

    uv run python -m kutu.vitrin          → http://localhost:8767/preview/vitrin.html

Her parça türünün geometrisi bir kez STL olarak yazılır (out/vitrin/geo/<id>.stl); bir tasarım,
bu geometrilere 4×4 dönüşüm matrisli örneklerden ve parça listesinden oluşur.
"""
import hashlib
import json
import os
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from build123d import Part, Pos, export_stl

from kutu import params as p
from kutu.montaj import Yerlesim, evrensel_grup_ac, kutu
from kutu.parts import evrensel as ev

KOK = Path(__file__).resolve().parents[2]
GEO = KOK / "out" / "vitrin" / "geo"

ADLAR = {"taban": "Taban karosu", "cerceve_hucre": "Çerçeve hücresi", "kapak_hucre": "Kapak hücresi",
         "kam_cerceve": "Kam (çerçeve)", "kam_kapak": "Kam (kapak)", "tapa": "Tapa",
         "mentese_cerceve": "Menteşe eki (çerçeve)", "mentese_kapak": "Menteşe eki (kapak)",
         "mentese_pimi": "Menteşe pimi", "mandal_eki": "Mandal eki", "kulp_ayagi": "Kulp ayağı",
         "kulp_kolu": "Kulp kolu", "kulp_cubugu": "Kulp çubuğu", "kose": "Köşe", "kiskac": "Kıskaç",
         "panel": "Panel", "yatay_kiskac": "Yatay kıskaç", "kose_dugumu": "Köşe düğümü",
         "kiskac_dugumu": "Kıskaç düğümü", "cekmece": "Çekmece", "raf": "Raf"}
HAZIR = {"kulp_cubugu", "mentese_pimi"}       # stok malzemeden boyuna kesilir
DUZENLER = ("tek", "bloklar", "satir", "node")
CEKMECE_DISARI = 0.6 * p.P_XY     # "çekmeceler dışarıda" görünümünde öne çekilme
KAPAK_ACI = 90.0


def kapak_duzeni(nx: int, ny: int, duzen: str) -> list[tuple[int, int, int, int]]:
    """Kapak grupları. bloklar: önce 2×2, sonra 2×1, kalan 1×1."""
    if duzen == "tek":
        return [(0, 0, nx, ny)]
    if duzen == "satir":
        return [(0, j, nx, 1) for j in range(ny)]
    if duzen == "node":
        return [(i, j, 1, 1) for j in range(ny) for i in range(nx)]
    dolu: set[tuple[int, int]] = set()
    out = []
    for j in range(ny):
        for i in range(nx):
            if (i, j) in dolu:
                continue
            for gx, gy in ((2, 2), (2, 1), (1, 1)):
                hucre = {(a, b) for a in range(i, i + gx) for b in range(j, j + gy)}
                if i + gx <= nx and j + gy <= ny and not hucre & dolu:
                    out.append((i, j, gx, gy))
                    dolu |= hucre
                    break
    return out


def _matris(loc) -> list[float]:
    t = loc.wrapped.Transformation()
    return [t.Value(r, c) for r in (1, 2, 3) for c in (1, 2, 3, 4)] + [0.0, 0.0, 0.0, 1.0]


class Katalog:
    """Benzersiz geometriler: aynı TShape'i paylaşan (yalnız konumu farklı) parçalar tek STL."""

    def __init__(self, klasor: Path = GEO):
        self.klasor = klasor
        klasor.mkdir(parents=True, exist_ok=True)
        self._refs: list[tuple[Part, str]] = []
        self._sekil: dict[str, Part] = {}

    def bul(self, parca: Part) -> tuple[Part, str]:
        for ref, gid in self._refs:
            if ref.wrapped.IsPartner(parca.wrapped):
                return ref, gid
        with tempfile.TemporaryDirectory() as d:
            gecici = Path(d) / "g.stl"
            export_stl(parca, str(gecici))
            veri = gecici.read_bytes()
        gid = hashlib.sha1(veri).hexdigest()[:12]
        hedef = self.klasor / f"{gid}.stl"
        if not hedef.exists():          # paralel üretimde yarım dosya görünmesin
            gecici = hedef.with_suffix(f".{os.getpid()}.tmp")
            gecici.write_bytes(veri)
            os.replace(gecici, hedef)
        self._refs.append((parca, gid))
        self._sekil.setdefault(gid, parca)
        return parca, gid

    def sekil(self, gid: str) -> Part:
        return self._sekil[gid]


def _olcu(tur: str, sekil: Part) -> str:
    bb = sekil.bounding_box()
    if tur == "kulp_cubugu":
        L = bb.size.X
        return (f"{p.KULP_CUBUK_W:g}×{p.KULP_CUBUK_T:g} alüminyum yassı · kesim {L:g} mm "
                f"(pim arası {L - 2 * ev.KULP_CUBUK_UC:g})")
    if tur == "mentese_pimi":
        return f"Ø{2 * p.MENTESE_PIM_R:g} çelik pim · {bb.size.X:g} mm"
    a = sorted((bb.size.X, bb.size.Y, bb.size.Z), reverse=True)
    return "×".join(f"{round(v, 1):g}" for v in a) + " mm"


def tasarim(katalog: Katalog, nx: int, ny: int, nz: int, kulp: bool, cekmece: bool,
            duzen: str = "tek", kapak_acik: bool = False, kulp_acik: bool = False,
            cekmece_disari: bool = False) -> dict:
    """Görünüm seçenekleri (kapak_acik, kulp_acik, cekmece_disari) yalnız konumları değiştirir."""
    gruplar = kapak_duzeni(nx, ny, duzen)
    liste = kutu(nx, ny, nz, kulp=kulp, kulp_acik=kulp_acik, cekmece=cekmece, kapak_gruplari=gruplar,
                 mandal_acik=kapak_acik)
    if kapak_acik:          # bütün gruplar açıkken her grup tam açılır
        yeni = {}
        for g in range(len(gruplar)):
            yeni |= {y.ad: y for y in evrensel_grup_ac(liste, g, KAPAK_ACI, nx, ny, nz, gruplar)}
        liste = [yeni.get(y.ad, y) for y in liste]
    if cekmece_disari:
        liste = [Yerlesim(y.ad, y.tur, Pos(0, -CEKMECE_DISARI, 0) * y.parca, y.patlat)
                 if y.tur == "cekmece" else y for y in liste]
    parcalar, satir = [], {}
    for y in liste:
        ref, gid = katalog.bul(y.parca)
        rel = y.parca.location * ref.location.inverse()
        parcalar.append({"ad": y.ad, "tur": y.tur, "geo": gid, "m": _matris(rel),
                         "patlat": list(y.patlat)})
        olcu = _olcu(y.tur, ref)
        r = satir.setdefault((y.tur, olcu), {"tur": y.tur, "ad": ADLAR.get(y.tur, y.tur), "olcu": olcu,
                                             "hazir": y.tur in HAZIR, "adet": 0})
        r["adet"] += 1
    uyari: list[str] = []
    return {"nx": nx, "ny": ny, "nz": nz, "kulp": kulp, "cekmece": cekmece, "duzen": duzen,
            "gruplar": gruplar, "parcalar": parcalar, "liste": list(satir.values()), "uyari": uyari,
            "P_XY": p.P_XY, "P_Z": p.P_Z}


_KATALOG: Katalog | None = None
_KILIT = threading.Lock()


class _Isleyici(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(KOK), **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        u = urlparse(self.path)
        if u.path != "/api/tasarim":
            return super().do_GET()
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            nx, ny, nz = (max(1, min(8, int(q.get(k, 1)))) for k in ("nx", "ny", "nz"))
            duzen = q.get("duzen", "tek")
            if duzen not in DUZENLER:
                raise ValueError(f"düzen: {duzen}")
            with _KILIT:
                global _KATALOG
                _KATALOG = _KATALOG or Katalog()
                bayrak = {k: q.get(k) == "1" for k in ("kulp", "cekmece", "kapak_acik", "kulp_acik",
                                                    "cekmece_disari")}
                veri = tasarim(_KATALOG, nx, ny, nz, duzen=duzen, **bayrak)
            govde, kod = json.dumps(veri, ensure_ascii=False).encode(), 200
        except Exception as e:  # noqa: BLE001 — hatayı arayüze ilet
            govde, kod = json.dumps({"hata": str(e)}, ensure_ascii=False).encode(), 400
        self.send_response(kod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(govde)))
        self.end_headers()
        self.wfile.write(govde)


def main(port: int = 8767) -> None:
    print(f"http://localhost:{port}/preview/vitrin.html")
    ThreadingHTTPServer(("", port), _Isleyici).serve_forever()


if __name__ == "__main__":
    main()
