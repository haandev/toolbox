# Faz 0–2 Temel Parçalar — Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Panel, köşe, kıskaç ve karo parçalarını build123d ile parametrik üretmek, bunlardan `kutu(nx, ny, nz)` montajını kurmak, STEP/STL çıktısı almak ve tarayıcıda Three.js ile göstermek.

**Architecture:** Tüm ölçüler `src/kutu/params.py`'de. Her parça kendi yerel koordinatında bir fonksiyon (`panel()`, `kose()`, `kiskac()`, `karo()`); paylaşılan geometri `src/kutu/lib/` altında. `montaj.py` parçaları dünya koordinatına yerleştirir; `export.py` STEP/STL ve önizleme için konumlu STL + `manifest.json` üretir. `preview/index.html` manifest'i okuyup sahneyi kurar.

**Tech Stack:** Python 3.12, uv, build123d (OpenCascade), pytest, Three.js 0.160 (CDN).

**Spec:** `docs/specs/2026-10-01-faz0-2-temel-parcalar.md`

## Global Constraints

- Tüm ölçüler mm; parça dosyalarında sabit sayı yok — hepsi `params.py`'den.
- Izgara: `P_XY = 200`, `P_Z = 100`, `U = 160`, `H = 80`, `GAP = 0.5`; `K = 20`, `T = 10` türetilir.
- Kalıp: `WALL = 2.5`, `RIB = 1.5`, `DRAFT_OUT = 1.5°`, `DRAFT_IN = 1.0°`, `FIT = 0.2`.
- Tek vida boyu: 4 mm plastik vida (kule deliği `0.8 × 4 = 3.2`); `PROTO = True` iken M3 heat-set insert deliği (4.0 mm).
- Koordinat: CAD'de Z yukarı. Kutu orijini (0,0,0) = alt-güneybatı nominal ızgara köşesi.
- `build123d >= 0.9`, Python `>=3.10,<3.14`.
- Kilit noktaları: her node yüzünün merkezi. Bu planda kilit geometrisi yok; yalnızca kilit bölgesi boş bırakılır.
- `out/` git'e girmez.

## Spec'ten uygulama düzeyindeki netleştirmeler

Bu kararlar plan yazılırken geometri hesabından çıktı; Task 10'da spec'e işlenir:

1. **Panel parça boyu `U + 2·DIL = 172`, yüksekliği `H + 2·DIL = 92`.** `U`/`H` görünür açıklık (adım); panelin dilleri (`DIL = 6`) köşe/kıskaç kanalına ve karo oluğuna girer.
2. **Kenar boncuğu yerine düz dil.** Panel her yönden kanal/olukla sarıldığı için boncuk tutuculuk katmıyor; dil kalınlığı = `WALL`.
3. **Panel dış yüzü `LIP = 1.5` mm içeride.** Kanalın dış dudağı olmadan panel dışarı düşer; panel dış yüzü köşe/kıskaç yüzünden 1.5 mm gömük.
4. **Kalıp eğimi bu fazda geometriye uygulanmaz**; `kalip.py` eğimsiz yüzleri raporlar. Eğim uygulaması kalıp hazırlık fazına kalır.
5. **Önizleme GLB yerine konumlu STL + manifest kullanır** (birim karmaşası yok, renkler manifest'ten).
6. Prototip kuponları `src/kutu/prototip.py`'de (test edilebilir modül), çıktısı `out/prototip/`.

## Review Focus

1. **Kare olmayan kutular (nx ≠ ny):** döndürülmüş köşe/panel/kıskaç yerleşimi çakışmasız olmalı → Task 7'de `kutu(2,1,1)` çakışma testi.
2. **2H kutular (nz = 2):** iki kat sırt sırta karo ile kurulur, dış ölçü 200×200×200−1 olmalı → Task 7'de `kutu(1,1,2)` ölçü + çakışma testi.
3. **`PROTO = False` (seri üretim) modu:** kule deliği 3.2 mm'ye dönmeli → Task 2'de monkeypatch testi.
4. **Değen ama kesişmeyen parçalar** (köşe karoya oturur): çakışma ölçümü 0 dönmeli, hata vermemeli → Task 7'de değen kutular testi.
5. **Büyük kutu (2×2):** parça sayısı ve dış ölçü doğru, kıskaçlar dört yanda → Task 7'de `kutu(2,2,1)` sayım testi.

---

## Dosya yapısı

```
toolbox/
├── pyproject.toml
├── .python-version
├── .claude/launch.json          (Task 9'da güncellenir)
├── src/kutu/
│   ├── __init__.py
│   ├── params.py                (Task 1)
│   ├── kalip.py                 (Task 1 — eğimsiz yüz raporu)
│   ├── lib/
│   │   ├── __init__.py          (MIN3 hizalama sabiti)
│   │   ├── kanal.py             (yuva/oluk kesit aralığı + yuva kutusu)
│   │   ├── kule.py              (vida kulesi)
│   │   └── kilit_yeri.py        (kilit bölgeleri + kilit noktaları)
│   ├── parts/
│   │   ├── __init__.py
│   │   ├── panel.py
│   │   ├── kose.py
│   │   ├── kiskac.py
│   │   └── karo.py
│   ├── montaj.py
│   ├── export.py
│   └── prototip.py
├── tests/
│   ├── test_params.py
│   ├── test_lib.py
│   ├── test_panel.py
│   ├── test_kose.py
│   ├── test_kiskac.py
│   ├── test_karo.py
│   ├── test_montaj.py
│   ├── test_export.py
│   └── test_prototip.py
└── preview/index.html
```

---

### Task 1: Proje iskeleti, parametreler ve kalıp raporu

**Files:**
- Create: `pyproject.toml`, `.python-version`, `src/kutu/__init__.py`, `src/kutu/params.py`, `src/kutu/kalip.py`
- Test: `tests/test_params.py`

**Interfaces:**
- Produces: `kutu.params` sabitleri (aşağıdaki dosyada tam liste), `params.kutu_dis(n: int, adim: float) -> float`, `kutu.kalip.egimsiz_yuz_sayisi(parca: Part, cekme: tuple[float,float,float]) -> int`

- [ ] **Step 1: Proje dosyalarını oluştur**

`pyproject.toml`:
```toml
[project]
name = "kutu"
version = "0.1.0"
description = "Modüler kutu sistemi parametrik parçaları"
requires-python = ">=3.10,<3.14"
dependencies = ["build123d>=0.9"]

[dependency-groups]
dev = ["pytest>=8"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/kutu"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`.python-version`:
```
3.12
```

`src/kutu/__init__.py`: boş dosya.

Run: `uv sync`
Expected: build123d ve pytest kurulur, hata yok.

- [ ] **Step 2: Failing test yaz**

`tests/test_params.py`:
```python
import pytest
from build123d import Box
from kutu import params as p
from kutu.kalip import egimsiz_yuz_sayisi


def test_turetilen_degerler():
    assert p.K == 20
    assert p.T == 10
    assert p.PANEL_L == 172
    assert p.PANEL_H == 92


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_yatay_izgara_esitligi(n):
    # köşe + n panel + (n-1) kıskaç + köşe = n adım
    assert p.K + n * p.U + (n - 1) * 2 * p.K + p.K == n * p.P_XY


@pytest.mark.parametrize("m", [1, 2, 3])
def test_dikey_izgara_esitligi(m):
    # taban + m panel + (m-1) sırt sırta karo çifti + tavan = m adım
    assert p.T + m * p.H + (m - 1) * 2 * p.T + p.T == m * p.P_Z


def test_kutu_dis_olcusu():
    assert p.kutu_dis(1, p.P_XY) == 199
    assert p.kutu_dis(2, p.P_XY) == 399
    assert p.kutu_dis(1, p.P_Z) == 99


def test_kalip_kurallari():
    assert p.RIB == pytest.approx(0.6 * p.WALL)
    assert p.R_IN_MIN == pytest.approx(0.5 * p.WALL)


def test_cep_kule_sigar():
    # köşe cebi kuleyi almalı
    cep = (p.K - p.WALL) - p.CEP_IC
    assert cep > p.KULE_OD
    # kıskaç kuleleri cebe sığmalı ve birbirine değmemeli
    assert p.KISKAC_KULE_X + p.KULE_OD / 2 < p.KISKAC_CEP_YARI
    assert p.KISKAC_KULE_X - p.KULE_OD / 2 > 0


def test_egimsiz_yuz_sayisi_kutu():
    # Z yönünde çekilen düz kutunun 4 yan yüzü eğimsizdir
    assert egimsiz_yuz_sayisi(Box(10, 10, 10), (0, 0, 1)) == 4
```

- [ ] **Step 3: Testin düştüğünü gör**

Run: `uv run pytest tests/test_params.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kutu.params'`

- [ ] **Step 4: `params.py` ve `kalip.py` yaz**

`src/kutu/params.py`:
```python
"""Modüler kutu sistemi — tüm ölçüler (mm). Parça dosyalarında sabit sayı yazılmaz."""

# --- Izgara (girdi) ---
P_XY = 200.0   # yatay node adımı
P_Z = 100.0    # dikey node adımı
U = 160.0      # panel adımı (görünür açıklık)
H = 80.0       # panel yüksekliği (görünür açıklık)
GAP = 0.5      # komşu kutular arası taraf başı boşluk

# --- Türetilen ---
K = (P_XY - U) / 2   # köşe katkısı (20); kıskaç genişliği 2K
T = (P_Z - H) / 2    # karo katkısı (10)

# --- Kalıp kuralları ---
WALL = 2.5
RIB = 0.6 * WALL
RIB_D = 6.0          # kaburga derinliği (deriden içeri)
DRAFT_OUT = 1.5      # derece
DRAFT_IN = 1.0       # derece
R_IN_MIN = 0.5 * WALL
FIT = 0.2            # geçme boşluğu, prototiple kalibre edilir

# --- Kanal / dil ---
LIP = 1.5                  # kanal dış dudağı; panel dış yüzü bu kadar gömük
DIL = 6.0                  # panel dilinin kanal/oluk içine giriş boyu
PANEL_L = U + 2 * DIL      # 172
PANEL_H = H + 2 * DIL      # 92
PANEL_KABURGA_X = (-55.0, -35.0, 35.0, 55.0)   # dikey kaburga konumları (panel merkezine göre)

# --- Vida / kule ---
PROTO = True               # True: heat-set insert deliği (prototip)
VIDA_D = 4.0
KULE_OD = 8.5
KULE_DELIK = 0.8 * VIDA_D  # seri üretim, plastik vida (3.2)
INSERT_DELIK = 4.0         # M3 heat-set insert
GECIS_DELIK = 4.5          # karo vida geçiş deliği

# --- Köşe / kıskaç cepleri ---
CEP_IC = GAP + LIP + WALL + FIT + WALL      # dış yüzden cebe mesafe (7.2)
CEP_BOY = (H - WALL) / 2                     # alt ve üst cep derinliği; ortada WALL kalınlığında ara duvar
KOSE_R = 5.0                                 # köşe dış yuvarlatma
KOSE_KULE = (CEP_IC + (K - WALL)) / 2        # köşe kulesinin x=y konumu
KISKAC_CEP_YARI = K - DIL - FIT - WALL       # kıskaç cebinin yarı genişliği (11.3)
KISKAC_KULE_X = KISKAC_CEP_YARI - KULE_OD / 2 - 0.5   # kıskaç kuleleri ±x

# --- Karo ---
KARO_RIB_ARALIK = 40.0

# --- Kilit bölgeleri (bu fazda boş bırakılan hacim) ---
KILIT_W = 60.0     # panel üzerinde yatay
KILIT_H = 50.0     # panel üzerinde dikey
KILIT_KARO = 60.0  # karo üzerinde kare


def kutu_dis(n: int, adim: float) -> float:
    """n node'luk kenarın gerçek dış ölçüsü."""
    return n * adim - 2 * GAP
```

`src/kutu/kalip.py`:
```python
"""Kalıplanabilirlik raporları."""
from build123d import GeomType, Part, Vector


def egimsiz_yuz_sayisi(parca: Part, cekme: tuple[float, float, float]) -> int:
    """Çekme yönüne tam paralel (eğimsiz) düzlemsel yüzlerin sayısı."""
    yon = Vector(*cekme).normalized()
    sayi = 0
    for yuz in parca.faces():
        if yuz.geom_type != GeomType.PLANE:
            continue
        if abs(yuz.normal_at().dot(yon)) < 1e-6:
            sayi += 1
    return sayi
```

- [ ] **Step 5: Testlerin geçtiğini gör**

Run: `uv run pytest tests/test_params.py -v`
Expected: tümü PASS

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .python-version uv.lock src/kutu/__init__.py src/kutu/params.py src/kutu/kalip.py tests/test_params.py
git commit -m "Proje iskeleti, parametreler ve kalıp eğim raporu"
```

---

### Task 2: Paylaşılan geometri (kanal, kule, kilit yeri)

**Files:**
- Create: `src/kutu/lib/__init__.py`, `src/kutu/lib/kanal.py`, `src/kutu/lib/kule.py`, `src/kutu/lib/kilit_yeri.py`
- Test: `tests/test_lib.py`

**Interfaces:**
- Consumes: `kutu.params`
- Produces:
  - `kutu.lib.MIN3` — `(Align.MIN, Align.MIN, Align.MIN)`
  - `kanal.panel_y() -> tuple[float, float]` — panel derisinin içe doğru y aralığı `(GAP+LIP, GAP+LIP+WALL)`
  - `kanal.yuva_y() -> tuple[float, float]` — kanal/oluk boşluğunun y aralığı (panel ± FIT)
  - `kanal.yuva(x0: float, x1: float, z0: float, z1: float) -> Part` — y aralığı `yuva_y()` olan kesme kutusu
  - `kule.delik_capi() -> float`
  - `kule.kule(boy: float) -> Part` — z=0'dan +z'ye uzanan, deliği z=0'da açık silindir kule
  - `kilit_yeri.panel_bolgesi() -> Part` — panel yerel çerçevesinde kaburgasız bırakılacak hacim
  - `kilit_yeri.karo_bolgesi() -> Part` — karo yerel çerçevesinde kaburgasız bırakılacak hacim
  - `kilit_yeri.kilit_noktalari(nx: int, ny: int, nz: int) -> list[tuple[str, tuple[float, float, float]]]` — `(yüz, merkez)`; yüz ∈ `{"guney","kuzey","bati","dogu","alt","ust"}`

- [ ] **Step 1: Failing test yaz**

`tests/test_lib.py`:
```python
import pytest
from kutu import params as p
from kutu.lib import kanal, kule, kilit_yeri


def test_yuva_paneli_fit_ile_sarar():
    py0, py1 = kanal.panel_y()
    y0, y1 = kanal.yuva_y()
    assert py1 - py0 == pytest.approx(p.WALL)
    assert py0 - y0 == pytest.approx(p.FIT)
    assert y1 - py1 == pytest.approx(p.FIT)


def test_yuva_kutusu_olculeri():
    b = kanal.yuva(0, 10, 0, 20).bounding_box()
    y0, y1 = kanal.yuva_y()
    assert b.min.Y == pytest.approx(y0)
    assert b.max.Y == pytest.approx(y1)
    assert b.size.X == pytest.approx(10)
    assert b.size.Z == pytest.approx(20)


def test_kule_proto_insert_deligi():
    assert kule.delik_capi() == p.INSERT_DELIK


def test_kule_seri_uretim_deligi(monkeypatch):
    monkeypatch.setattr(p, "PROTO", False)
    assert kule.delik_capi() == pytest.approx(3.2)


def test_kule_geometrisi():
    k = kule.kule(20)
    assert k.is_valid()
    b = k.bounding_box()
    assert b.size.X == pytest.approx(p.KULE_OD)
    assert b.min.Z == pytest.approx(0)
    assert b.max.Z == pytest.approx(20)
    # delik var: hacim dolu silindirden küçük
    import math
    dolu = math.pi * (p.KULE_OD / 2) ** 2 * 20
    assert k.volume < dolu


def test_kilit_noktalari_tek_node():
    nk = kilit_yeri.kilit_noktalari(1, 1, 1)
    assert len(nk) == 6
    d = dict(nk)
    assert d["guney"] == (100, 0, 50)
    assert d["kuzey"] == (100, 200, 50)
    assert d["bati"] == (0, 100, 50)
    assert d["dogu"] == (200, 100, 50)
    assert d["alt"] == (100, 100, 0)
    assert d["ust"] == (100, 100, 100)


@pytest.mark.parametrize("nx,ny,nz", [(2, 1, 1), (2, 2, 1), (1, 1, 2), (3, 2, 2)])
def test_kilit_noktalari_sayisi_ve_izgara(nx, ny, nz):
    nk = kilit_yeri.kilit_noktalari(nx, ny, nz)
    assert len(nk) == 2 * (nx + ny) * nz + 2 * nx * ny
    for yuz, (x, y, z) in nk:
        # tüm kilit noktaları node yüz merkezlerinde
        if yuz in ("guney", "kuzey"):
            assert (x - 100) % 200 == 0 and (z - 50) % 100 == 0
        elif yuz in ("bati", "dogu"):
            assert (y - 100) % 200 == 0 and (z - 50) % 100 == 0
        else:
            assert (x - 100) % 200 == 0 and (y - 100) % 200 == 0


def test_panel_bolgesi_merkezde():
    b = kilit_yeri.panel_bolgesi().bounding_box()
    assert b.center().X == pytest.approx(0)
    assert b.center().Z == pytest.approx(p.T + p.H / 2)
    assert b.size.X == pytest.approx(p.KILIT_W)
    assert b.size.Z == pytest.approx(p.KILIT_H)


def test_karo_bolgesi_merkezde():
    b = kilit_yeri.karo_bolgesi().bounding_box()
    assert b.center().X == pytest.approx(p.P_XY / 2)
    assert b.center().Y == pytest.approx(p.P_XY / 2)
    assert b.size.X == pytest.approx(p.KILIT_KARO)
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `uv run pytest tests/test_lib.py -v`
Expected: FAIL — `ImportError: cannot import name 'kanal' from 'kutu.lib'`

- [ ] **Step 3: Modülleri yaz**

`src/kutu/lib/__init__.py`:
```python
from build123d import Align

MIN3 = (Align.MIN, Align.MIN, Align.MIN)
```

`src/kutu/lib/kanal.py`:
```python
"""Panel dili ile köşe/kıskaç kanalı ve karo oluğu arasındaki ortak kesit.

Yerel çerçeve: y = 0 kutunun nominal dış yüzü, +y kutunun içi.
"""
from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3


def panel_y() -> tuple[float, float]:
    y0 = p.GAP + p.LIP
    return (y0, y0 + p.WALL)


def yuva_y() -> tuple[float, float]:
    y0, y1 = panel_y()
    return (y0 - p.FIT, y1 + p.FIT)


def yuva(x0: float, x1: float, z0: float, z1: float) -> Part:
    y0, y1 = yuva_y()
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN3)
```

`src/kutu/lib/kule.py`:
```python
"""Vida kulesi: seri üretimde plastik vida, prototipte heat-set insert."""
from build123d import Align, Cylinder, Part

from kutu import params as p

_ALT = (Align.CENTER, Align.CENTER, Align.MIN)


def delik_capi() -> float:
    return p.INSERT_DELIK if p.PROTO else p.KULE_DELIK


def kule(boy: float) -> Part:
    """z=0'dan +z'ye uzanan kule; delik z=0'da açık, üstte WALL kadar kör."""
    dis = Cylinder(p.KULE_OD / 2, boy, align=_ALT)
    delik = Cylinder(delik_capi() / 2, boy - p.WALL, align=_ALT)
    return dis - delik
```

`src/kutu/lib/kilit_yeri.py`:
```python
"""Kilit bölgeleri (bu fazda boş bırakılan hacim) ve kilit noktası ızgarası."""
from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y


def panel_bolgesi() -> Part:
    """Panel yerel çerçevesinde (x merkezli), deri arkasında kaburgasız kalacak hacim."""
    _, y_ic = panel_y()
    return Pos(-p.KILIT_W / 2, y_ic, p.T + (p.H - p.KILIT_H) / 2) * Box(
        p.KILIT_W, p.RIB_D, p.KILIT_H, align=MIN3
    )


def karo_bolgesi() -> Part:
    """Karo yerel çerçevesinde, merkezde kaburgasız kalacak hacim (güverte altı)."""
    a = (p.P_XY - p.KILIT_KARO) / 2
    return Pos(a, a, p.GAP) * Box(p.KILIT_KARO, p.KILIT_KARO, p.T - p.GAP - p.WALL, align=MIN3)


def kilit_noktalari(nx: int, ny: int, nz: int) -> list[tuple[str, tuple[float, float, float]]]:
    W, D, Hh = nx * p.P_XY, ny * p.P_XY, nz * p.P_Z
    hx = p.P_XY / 2
    hz = p.P_Z / 2
    out: list[tuple[str, tuple[float, float, float]]] = []
    for k in range(nz):
        z = hz + k * p.P_Z
        for i in range(nx):
            x = hx + i * p.P_XY
            out.append(("guney", (x, 0, z)))
            out.append(("kuzey", (x, D, z)))
        for j in range(ny):
            y = hx + j * p.P_XY
            out.append(("bati", (0, y, z)))
            out.append(("dogu", (W, y, z)))
    for i in range(nx):
        for j in range(ny):
            x, y = hx + i * p.P_XY, hx + j * p.P_XY
            out.append(("alt", (x, y, 0)))
            out.append(("ust", (x, y, Hh)))
    return out
```

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `uv run pytest tests/test_lib.py -v`
Expected: tümü PASS

- [ ] **Step 5: Commit**

```bash
git add src/kutu/lib tests/test_lib.py
git commit -m "Ortak geometri: kanal, vida kulesi, kilit yeri"
```

---

### Task 3: Duvar paneli

**Files:**
- Create: `src/kutu/parts/__init__.py` (boş), `src/kutu/parts/panel.py`
- Test: `tests/test_panel.py`

**Interfaces:**
- Consumes: `kanal.panel_y`, `kilit_yeri.panel_bolgesi`, `MIN3`
- Produces: `kutu.parts.panel.panel() -> Part`. Yerel çerçeve: x merkezli (`±PANEL_L/2`), y içe (deri `panel_y()` aralığında), z kutu yüksekliği (`T−DIL … T+H+DIL`). Kalıp çekme yönü yerel +y.

- [ ] **Step 1: Failing test yaz**

`tests/test_panel.py`:
```python
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
    assert pnl.is_valid()


def test_dis_olculer(pnl):
    b = pnl.bounding_box()
    y0, _ = panel_y()
    assert b.size.X == pytest.approx(p.PANEL_L)
    assert b.size.Z == pytest.approx(p.PANEL_H)
    assert b.min.Z == pytest.approx(p.T - p.DIL)
    assert b.min.Y == pytest.approx(y0)
    assert b.size.Y == pytest.approx(p.WALL + p.RIB_D)


def test_deri_kalinligi_wall(pnl):
    # kilit bölgesinin ortasında yalnızca deri var
    y0, y1 = panel_y()
    sonda = Pos(-5, y0 - 1, p.T + p.H / 2 - 5) * Box(10, p.WALL + p.RIB_D + 2, 10, align=MIN3)
    kesit = pnl & sonda
    assert kesit.volume == pytest.approx(10 * 10 * p.WALL, rel=1e-3)


def test_kilit_bolgesinde_kaburga_yok(pnl):
    assert (pnl & panel_bolgesi()).volume == pytest.approx(0, abs=1e-6)


def test_kaburgalar_kanala_girmez(pnl):
    # dil bölgesinde (|x| > U/2) yalnızca deri bulunur
    y0, _ = panel_y()
    dil = Pos(p.U / 2, y0, p.T - p.DIL) * Box(p.DIL, p.WALL + p.RIB_D, p.PANEL_H, align=MIN3)
    assert (pnl & dil).volume == pytest.approx(p.DIL * p.WALL * p.PANEL_H, rel=1e-3)
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `uv run pytest tests/test_panel.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kutu.parts'`

- [ ] **Step 3: Paneli yaz**

`src/kutu/parts/__init__.py`: boş dosya.

`src/kutu/parts/panel.py`:
```python
"""Duvar paneli: düz deri + iç kaburgalar; dört kenarda dil."""
from functools import cache

from build123d import Box, Part, Pos

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import panel_y
from kutu.lib.kilit_yeri import panel_bolgesi


@cache
def panel() -> Part:
    y0, y_ic = panel_y()
    deri = Pos(-p.PANEL_L / 2, y0, p.T - p.DIL) * Box(p.PANEL_L, p.WALL, p.PANEL_H, align=MIN3)

    # kaburgalar yalnızca görünür açıklıkta (kanal/oluk içine girmez), 1 mm pay
    z0, z1 = p.T + 1, p.T + p.H - 1
    x_yari = p.U / 2 - 1
    kaburga = Pos(-x_yari, y_ic, p.T + p.H / 2 - p.RIB / 2) * Box(2 * x_yari, p.RIB_D, p.RIB, align=MIN3)
    for x in p.PANEL_KABURGA_X:
        kaburga += Pos(x - p.RIB / 2, y_ic, z0) * Box(p.RIB, p.RIB_D, z1 - z0, align=MIN3)
    kaburga -= panel_bolgesi()

    return deri + kaburga
```

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `uv run pytest tests/test_panel.py -v`
Expected: tümü PASS

- [ ] **Step 5: Commit**

```bash
git add src/kutu/parts/__init__.py src/kutu/parts/panel.py tests/test_panel.py
git commit -m "Duvar paneli"
```

---

### Task 4: Köşe

**Files:**
- Create: `src/kutu/parts/kose.py`
- Test: `tests/test_kose.py`

**Interfaces:**
- Consumes: `kanal.yuva`, `kule.kule`, `MIN3`
- Produces: `kutu.parts.kose.kose() -> Part`. Yerel çerçeve: kutunun güneybatı köşesi; gövde `x, y ∈ [GAP, K]`, `z ∈ [T, T+H]`. Güney duvar kanalı +x yönüne, batı duvar kanalı +y yönüne açılır. Kalıp çekme yönü Z.

- [ ] **Step 1: Failing test yaz**

`tests/test_kose.py`:
```python
import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva_y
from kutu.parts.kose import kose


@pytest.fixture(scope="module")
def k():
    return kose()


def test_gecerli_kati(k):
    assert k.is_valid()


def test_dis_olculer(k):
    b = k.bounding_box()
    assert b.min.X == pytest.approx(p.GAP)
    assert b.min.Y == pytest.approx(p.GAP)
    assert b.max.X == pytest.approx(p.K)
    assert b.max.Y == pytest.approx(p.K)
    assert b.min.Z == pytest.approx(p.T)
    assert b.max.Z == pytest.approx(p.T + p.H)


def test_kanallar_bos(k):
    y0, y1 = yuva_y()
    guney = Pos(p.K - p.DIL, y0, p.T) * Box(p.DIL, y1 - y0, p.H, align=MIN3)
    bati = Pos(y0, p.K - p.DIL, p.T) * Box(y1 - y0, p.DIL, p.H, align=MIN3)
    assert (k & guney).volume == pytest.approx(0, abs=1e-6)
    assert (k & bati).volume == pytest.approx(0, abs=1e-6)


def test_ici_oyuk(k):
    dolu = (p.K - p.GAP) ** 2 * p.H
    assert k.volume < 0.75 * dolu


def test_vida_delikleri_uclarda_acik(k):
    # alt ve üst uçta kule ekseninde ince sonda boşta olmalı
    m = p.KOSE_KULE
    alt = Pos(m - 0.5, m - 0.5, p.T) * Box(1, 1, 3, align=MIN3)
    ust = Pos(m - 0.5, m - 0.5, p.T + p.H - 3) * Box(1, 1, 3, align=MIN3)
    assert (k & alt).volume == pytest.approx(0, abs=1e-6)
    assert (k & ust).volume == pytest.approx(0, abs=1e-6)
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `uv run pytest tests/test_kose.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kutu.parts.kose'`

- [ ] **Step 3: Köşeyi yaz**

`src/kutu/parts/kose.py`:
```python
"""Köşe: iki duvar kanalı, alt/üst cep ve vida kuleleri olan dikey profil."""
from functools import cache

from build123d import Axis, Box, Part, Pos, Rot, Vector

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva, yuva_y
from kutu.lib.kule import kule


def _bati_kanal() -> Part:
    """Güney kanalının x↔y yansıması: batı duvarının dili +y yönünde girer."""
    y0, y1 = yuva_y()
    x0 = p.K - p.DIL - p.FIT
    return Pos(y0, x0, p.T) * Box(y1 - y0, p.K - x0, p.H, align=MIN3)


@cache
def kose() -> Part:
    g = p.GAP
    govde = Pos(g, g, p.T) * Box(p.K - g, p.K - g, p.H, align=MIN3)
    dis_kenar = govde.edges().filter_by(Axis.Z).sort_by_distance(Vector(g, g, p.T))[0]
    govde = govde.fillet(p.KOSE_R, [dis_kenar])

    # güney kanalı (dil +x yönünde girer) ve batı kanalı (dil +y yönünde girer)
    govde -= yuva(p.K - p.DIL - p.FIT, p.K, p.T, p.T + p.H)
    govde -= _bati_kanal()

    # alt ve üst cepler, ortada WALL kalınlığında ara duvar
    c0, c1 = p.CEP_IC, p.K - p.WALL
    cep = Box(c1 - c0, c1 - c0, p.CEP_BOY, align=MIN3)
    govde -= Pos(c0, c0, p.T) * cep
    govde -= Pos(c0, c0, p.T + p.H - p.CEP_BOY) * cep

    m = p.KOSE_KULE
    govde += Pos(m, m, p.T) * kule(p.CEP_BOY)
    govde += Pos(m, m, p.T + p.H) * Rot(180, 0, 0) * kule(p.CEP_BOY)
    return govde
```

> Not: build123d'de `fillet` imzası sürüme göre `govde.fillet(radius, edge_list)` ya da `fillet(edges, radius)` olabilir; kurulu sürümün dokümanına göre kullan, sonuç aynı: yalnızca (GAP, GAP) dış dikey kenarı R5.

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `uv run pytest tests/test_kose.py -v`
Expected: tümü PASS

- [ ] **Step 5: Commit**

```bash
git add src/kutu/parts/kose.py tests/test_kose.py
git commit -m "Köşe parçası"
```

---

### Task 5: Kıskaç

**Files:**
- Create: `src/kutu/parts/kiskac.py`
- Test: `tests/test_kiskac.py`

**Interfaces:**
- Consumes: `kanal.yuva`, `kule.kule`, `MIN3`
- Produces: `kutu.parts.kiskac.kiskac() -> Part`. Yerel çerçeve: x merkezli (`±K`), y içe (`GAP … K`), z `T … T+H`. Güney duvarı üzerinde iki panelin ek yeri. Kalıp çekme yönü Z.

- [ ] **Step 1: Failing test yaz**

`tests/test_kiskac.py`:
```python
import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva_y
from kutu.parts.kiskac import kiskac


@pytest.fixture(scope="module")
def ks():
    return kiskac()


def test_gecerli_kati(ks):
    assert ks.is_valid()


def test_dis_olculer(ks):
    b = ks.bounding_box()
    assert b.size.X == pytest.approx(2 * p.K)
    assert b.min.X == pytest.approx(-p.K)
    assert b.min.Y == pytest.approx(p.GAP)
    assert b.max.Y == pytest.approx(p.K)
    assert b.min.Z == pytest.approx(p.T)
    assert b.max.Z == pytest.approx(p.T + p.H)


@pytest.mark.parametrize("taraf", [-1, 1])
def test_iki_yanda_kanal(ks, taraf):
    y0, y1 = yuva_y()
    x0 = p.K - p.DIL if taraf > 0 else -p.K
    sonda = Pos(x0, y0, p.T) * Box(p.DIL, y1 - y0, p.H, align=MIN3)
    assert (ks & sonda).volume == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("x", [-p.KISKAC_KULE_X, p.KISKAC_KULE_X])
def test_iki_kule_uclarda_acik(ks, x):
    m = (p.CEP_IC + p.K - p.WALL) / 2
    alt = Pos(x - 0.5, m - 0.5, p.T) * Box(1, 1, 3, align=MIN3)
    ust = Pos(x - 0.5, m - 0.5, p.T + p.H - 3) * Box(1, 1, 3, align=MIN3)
    assert (ks & alt).volume == pytest.approx(0, abs=1e-6)
    assert (ks & ust).volume == pytest.approx(0, abs=1e-6)
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `uv run pytest tests/test_kiskac.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kutu.parts.kiskac'`

- [ ] **Step 3: Kıskacı yaz**

`src/kutu/parts/kiskac.py`:
```python
"""Kıskaç: aynı düzlemdeki iki paneli ek yerinden birleştiren dikey profil."""
from functools import cache

from build123d import Box, Part, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva
from kutu.lib.kule import kule


@cache
def kiskac() -> Part:
    govde = Pos(-p.K, p.GAP, p.T) * Box(2 * p.K, p.K - p.GAP, p.H, align=MIN3)
    govde -= yuva(-p.K, -p.K + p.DIL + p.FIT, p.T, p.T + p.H)
    govde -= yuva(p.K - p.DIL - p.FIT, p.K, p.T, p.T + p.H)

    c0, c1 = p.CEP_IC, p.K - p.WALL
    cx = p.KISKAC_CEP_YARI
    cep = Box(2 * cx, c1 - c0, p.CEP_BOY, align=MIN3)
    govde -= Pos(-cx, c0, p.T) * cep
    govde -= Pos(-cx, c0, p.T + p.H - p.CEP_BOY) * cep

    m = (c0 + c1) / 2
    for x in (-p.KISKAC_KULE_X, p.KISKAC_KULE_X):
        govde += Pos(x, m, p.T) * kule(p.CEP_BOY)
        govde += Pos(x, m, p.T + p.H) * Rot(180, 0, 0) * kule(p.CEP_BOY)
    return govde
```

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `uv run pytest tests/test_kiskac.py -v`
Expected: tümü PASS

- [ ] **Step 5: Commit**

```bash
git add src/kutu/parts/kiskac.py tests/test_kiskac.py
git commit -m "Kıskaç parçası"
```

---

### Task 6: Karo (taban = tavan)

**Files:**
- Create: `src/kutu/parts/karo.py`
- Test: `tests/test_karo.py`

**Interfaces:**
- Consumes: `kanal.yuva`, `kilit_yeri.karo_bolgesi`, `MIN3`
- Produces: `kutu.parts.karo.karo() -> Part`. Yerel çerçeve: `x, y ∈ [GAP, P_XY−GAP]`, `z ∈ [GAP, T]`; oluk yüzü +z (taban konumu). Dört kenarda oluk, her köşede 3 vida geçiş deliği (köşe kulesi + iki komşu kıskaç kulesi). Kalıp çekme yönü Z.

- [ ] **Step 1: Failing test yaz**

`tests/test_karo.py`:
```python
import pytest
from build123d import Box, Cylinder, Align, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva_y
from kutu.lib.kilit_yeri import karo_bolgesi
from kutu.parts.karo import karo, delik_noktalari


@pytest.fixture(scope="module")
def kr():
    return karo()


def test_gecerli_kati(kr):
    assert kr.is_valid()


def test_dis_olculer(kr):
    b = kr.bounding_box()
    assert b.size.X == pytest.approx(p.P_XY - 2 * p.GAP)
    assert b.size.Y == pytest.approx(p.P_XY - 2 * p.GAP)
    assert b.min.Z == pytest.approx(p.GAP)
    assert b.max.Z == pytest.approx(p.T)


def test_guverte_wall_kalinliginda(kr):
    # kilit bölgesinin ortasında yalnızca güverte var
    c = p.P_XY / 2
    sonda = Pos(c - 5, c - 5, 0) * Box(10, 10, p.T, align=MIN3)
    assert (kr & sonda).volume == pytest.approx(10 * 10 * p.WALL, rel=1e-3)


def test_kilit_bolgesinde_kaburga_yok(kr):
    assert (kr & karo_bolgesi()).volume == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("aci", [0, 90, 180, 270])
def test_dort_kenarda_oluk(kr, aci):
    from build123d import Rot
    y0, y1 = yuva_y()
    oluk = Pos(p.K, y0, p.T - p.DIL) * Box(p.P_XY - 2 * p.K, y1 - y0, p.DIL, align=MIN3)
    c = p.P_XY / 2
    oluk = Pos(c, c, 0) * Rot(0, 0, aci) * Pos(-c, -c, 0) * oluk
    assert (kr & oluk).volume == pytest.approx(0, abs=1e-6)


def test_delik_noktalari_simetrik():
    n = delik_noktalari()
    assert len(n) == 12
    c = p.P_XY / 2
    kume = {(round(x, 3), round(y, 3)) for x, y in n}
    for x, y in n:
        # 90° döndürünce yine bir delik noktası
        assert (round(c - (y - c), 3), round(c + (x - c), 3)) in kume
        # y'de aynalayınca (tavan olarak ters çevirme) yine bir delik noktası
        assert (round(x, 3), round(p.P_XY - y, 3)) in kume


def test_delikler_acik(kr):
    for x, y in delik_noktalari():
        sonda = Pos(x, y, 0) * Cylinder(0.5, p.T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        assert (kr & sonda).volume == pytest.approx(0, abs=1e-6)
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `uv run pytest tests/test_karo.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kutu.parts.karo'`

- [ ] **Step 3: Karoyu yaz**

`src/kutu/parts/karo.py`:
```python
"""Karo: 1 node'luk taban/tavan plakası. Tavan, aynı parçanın ters çevrilmiş hâlidir."""
from functools import cache

from build123d import Align, Box, Cylinder, Part, Pos, Rot

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kanal import yuva
from kutu.lib.kilit_yeri import karo_bolgesi

_C = p.P_XY / 2


def _dondur(x: float, y: float, aci: int) -> tuple[float, float]:
    dx, dy = x - _C, y - _C
    for _ in range(aci // 90):
        dx, dy = -dy, dx
    return (_C + dx, _C + dy)


def delik_noktalari() -> list[tuple[float, float]]:
    """Her köşede: köşe kulesi + iki komşu kıskaç kulesi; 4 köşe → 12 delik."""
    m = p.KOSE_KULE
    km = (p.CEP_IC + p.K - p.WALL) / 2
    gb = [(m, m), (p.KISKAC_KULE_X, km), (km, p.KISKAC_KULE_X)]
    return [_dondur(x, y, a) for a in (0, 90, 180, 270) for x, y in gb]


@cache
def karo() -> Part:
    g = p.GAP
    L = p.P_XY - 2 * g
    plaka = Pos(g, g, g) * Box(L, L, p.T - g, align=MIN3)

    # iç bölge alttan boşaltılır, üstte WALL kalınlığında güverte kalır; kenarda K genişliğinde çerçeve
    ic_L = p.P_XY - 2 * p.K
    ic_h = p.T - g - p.WALL
    plaka -= Pos(p.K, p.K, g) * Box(ic_L, ic_L, ic_h, align=MIN3)

    # güverte altı kaburga ızgarası
    kaburga = None
    x = p.K + p.KARO_RIB_ARALIK
    while x < p.P_XY - p.K - 1e-6:
        dx = Pos(x - p.RIB / 2, p.K, g) * Box(p.RIB, ic_L, ic_h, align=MIN3)
        dy = Pos(p.K, x - p.RIB / 2, g) * Box(ic_L, p.RIB, ic_h, align=MIN3)
        kaburga = dx + dy if kaburga is None else kaburga + dx + dy
        x += p.KARO_RIB_ARALIK
    kaburga -= karo_bolgesi()
    plaka += kaburga

    # dört kenarda panel oluğu (üst yüzden DIL+FIT derin)
    oluk = yuva(g, p.P_XY - g, p.T - p.DIL - p.FIT, p.T)
    for aci in (0, 90, 180, 270):
        plaka -= Pos(_C, _C, 0) * Rot(0, 0, aci) * Pos(-_C, -_C, 0) * oluk

    # vida geçiş delikleri
    for x, y in delik_noktalari():
        plaka -= Pos(x, y, 0) * Cylinder(
            p.GECIS_DELIK / 2, p.T, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
    return plaka
```

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `uv run pytest tests/test_karo.py -v`
Expected: tümü PASS

- [ ] **Step 5: Commit**

```bash
git add src/kutu/parts/karo.py tests/test_karo.py
git commit -m "Karo (taban/tavan) parçası"
```

---

### Task 7: Montaj

**Files:**
- Create: `src/kutu/montaj.py`
- Test: `tests/test_montaj.py`

**Interfaces:**
- Consumes: `panel()`, `kose()`, `kiskac()`, `karo()`, `kilit_noktalari()`
- Produces:
  - `@dataclass Yerlesim(ad: str, tur: str, parca: Part, patlat: tuple[float, float, float])` — `tur ∈ {"karo","kose","kiskac","panel"}`, `parca` dünya koordinatında
  - `kutu(nx: int, ny: int, nz: int = 1) -> list[Yerlesim]`
  - `kesisim_hacmi(a: Part, b: Part) -> float`

Yerleşim kuralları (yerel → dünya, `Rot(0,0,θ)` saat yönü tersine):
- Panel/kıskaç: güney `Pos(x, 0, zb)`, kuzey `Pos(x, D, zb)·Rot(0,0,180)`, batı `Pos(0, y, zb)·Rot(0,0,−90)`, doğu `Pos(W, y, zb)·Rot(0,0,90)`.
- Köşe: GB `Pos(0,0,zb)`, GD `Pos(W,0,zb)·Rot(0,0,90)`, KD `Pos(W,D,zb)·Rot(0,0,180)`, KB `Pos(0,D,zb)·Rot(0,0,−90)`.
- Karo: taban `Pos(200i, 200j, zb)`, tavan `Pos(200i, 200j+200, zb+P_Z)·Rot(180,0,0)`.

- [ ] **Step 1: Failing test yaz**

`tests/test_montaj.py`:
```python
import itertools

import pytest
from build123d import Box, Pos
from kutu import params as p
from kutu.lib import MIN3
from kutu.montaj import kesisim_hacmi, kutu


def _sayim(liste):
    s = {}
    for y in liste:
        s[y.tur] = s.get(y.tur, 0) + 1
    return s


def _dis_kutu(liste):
    b = liste[0].parca.bounding_box()
    for y in liste[1:]:
        b = b.add(y.parca.bounding_box())
    return b


def _cakisma_yok(liste):
    for a, b in itertools.combinations(liste, 2):
        v = kesisim_hacmi(a.parca, b.parca)
        assert v < 1e-3, f"{a.ad} ile {b.ad} çakışıyor: {v:.3f} mm³"


def test_degen_kutular_sifir():
    a = Box(10, 10, 10, align=MIN3)
    b = Pos(10, 0, 0) * Box(10, 10, 10, align=MIN3)
    assert kesisim_hacmi(a, b) == pytest.approx(0, abs=1e-9)


def test_uzak_kutular_sifir():
    a = Box(10, 10, 10, align=MIN3)
    b = Pos(50, 0, 0) * Box(10, 10, 10, align=MIN3)
    assert kesisim_hacmi(a, b) == 0


def test_cakisan_kutular():
    a = Box(10, 10, 10, align=MIN3)
    b = Pos(5, 0, 0) * Box(10, 10, 10, align=MIN3)
    assert kesisim_hacmi(a, b) == pytest.approx(500)


@pytest.fixture(scope="module")
def k111():
    return kutu(1, 1, 1)


def test_tek_node_sayim(k111):
    assert _sayim(k111) == {"karo": 2, "kose": 4, "panel": 4}


def test_tek_node_dis_olcu(k111):
    b = _dis_kutu(k111)
    assert b.size.X == pytest.approx(p.kutu_dis(1, p.P_XY))
    assert b.size.Y == pytest.approx(p.kutu_dis(1, p.P_XY))
    assert b.size.Z == pytest.approx(p.kutu_dis(1, p.P_Z))
    assert b.min.X == pytest.approx(p.GAP)


def test_tek_node_cakisma_yok(k111):
    _cakisma_yok(k111)


def test_panel_kanalda_fit_boslugu(k111):
    paneller = [y for y in k111 if y.tur == "panel"]
    koseler = [y for y in k111 if y.tur == "kose"]
    karolar = [y for y in k111 if y.tur == "karo"]
    for pnl in paneller:
        en_yakin_kose = min(pnl.parca.distance_to(k.parca) for k in koseler)
        en_yakin_karo = min(pnl.parca.distance_to(k.parca) for k in karolar)
        assert en_yakin_kose == pytest.approx(p.FIT, abs=1e-3)
        assert en_yakin_karo == pytest.approx(p.FIT, abs=1e-3)


def test_kare_olmayan_kutu_2x1():
    k = kutu(2, 1, 1)
    assert _sayim(k) == {"karo": 4, "kose": 4, "panel": 6, "kiskac": 2}
    b = _dis_kutu(k)
    assert b.size.X == pytest.approx(p.kutu_dis(2, p.P_XY))
    assert b.size.Y == pytest.approx(p.kutu_dis(1, p.P_XY))
    _cakisma_yok(k)


def test_2h_kutu():
    k = kutu(1, 1, 2)
    assert _sayim(k) == {"karo": 4, "kose": 8, "panel": 8}
    b = _dis_kutu(k)
    assert b.size.Z == pytest.approx(p.kutu_dis(2, p.P_Z))
    _cakisma_yok(k)


def test_2x2_sayim_ve_olcu():
    k = kutu(2, 2, 1)
    assert _sayim(k) == {"karo": 8, "kose": 4, "panel": 8, "kiskac": 4}
    b = _dis_kutu(k)
    assert b.size.X == pytest.approx(p.kutu_dis(2, p.P_XY))
    assert b.size.Y == pytest.approx(p.kutu_dis(2, p.P_XY))


def test_patlatma_yonleri(k111):
    for y in k111:
        if y.tur == "karo":
            assert y.patlat[0] == 0 and y.patlat[1] == 0 and y.patlat[2] in (-1, 1)
        else:
            assert y.patlat[2] == 0 and (y.patlat[0], y.patlat[1]) != (0, 0)
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `uv run pytest tests/test_montaj.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kutu.montaj'`

- [ ] **Step 3: Montajı yaz**

`src/kutu/montaj.py`:
```python
"""Parçaları node ızgarasına yerleştirir: kutu(nx, ny, nz)."""
from dataclasses import dataclass

from build123d import Part, Pos, Rot

from kutu import params as p
from kutu.parts.karo import karo
from kutu.parts.kiskac import kiskac
from kutu.parts.kose import kose
from kutu.parts.panel import panel


@dataclass
class Yerlesim:
    ad: str
    tur: str
    parca: Part
    patlat: tuple[float, float, float]


def _isaret(v: float) -> int:
    return 0 if abs(v) < 1 else (1 if v > 0 else -1)


def kesisim_hacmi(a: Part, b: Part) -> float:
    ba, bb = a.bounding_box(), b.bounding_box()
    if (
        ba.max.X <= bb.min.X or bb.max.X <= ba.min.X
        or ba.max.Y <= bb.min.Y or bb.max.Y <= ba.min.Y
        or ba.max.Z <= bb.min.Z or bb.max.Z <= ba.min.Z
    ):
        return 0.0
    k = a & b
    return float(k.volume) if k is not None else 0.0


def kutu(nx: int, ny: int, nz: int = 1) -> list[Yerlesim]:
    W, D = nx * p.P_XY, ny * p.P_XY
    out: list[Yerlesim] = []

    def ekle(ad: str, tur: str, parca: Part, zb: float) -> None:
        c = parca.bounding_box().center()
        if tur == "karo":
            yon = (0, 0, _isaret(c.Z - (zb + p.P_Z / 2)))
        else:
            yon = (_isaret(c.X - W / 2), _isaret(c.Y - D / 2), 0)
        out.append(Yerlesim(ad, tur, parca, yon))

    for kat in range(nz):
        zb = kat * p.P_Z
        for i in range(nx):
            for j in range(ny):
                x0, y0 = i * p.P_XY, j * p.P_XY
                ekle(f"k{kat}_taban_{i}{j}", "karo", Pos(x0, y0, zb) * karo(), zb)
                ekle(f"k{kat}_tavan_{i}{j}", "karo",
                     Pos(x0, y0 + p.P_XY, zb + p.P_Z) * Rot(180, 0, 0) * karo(), zb)

        for ad, yer in (
            ("gb", Pos(0, 0, zb)),
            ("gd", Pos(W, 0, zb) * Rot(0, 0, 90)),
            ("kd", Pos(W, D, zb) * Rot(0, 0, 180)),
            ("kb", Pos(0, D, zb) * Rot(0, 0, -90)),
        ):
            ekle(f"k{kat}_kose_{ad}", "kose", yer * kose(), zb)

        def duvar(tur: str, parca: Part, x_listesi, y_listesi) -> None:
            for x in x_listesi:
                ekle(f"k{kat}_{tur}_g{x:g}", tur, Pos(x, 0, zb) * parca, zb)
                ekle(f"k{kat}_{tur}_k{x:g}", tur, Pos(x, D, zb) * Rot(0, 0, 180) * parca, zb)
            for y in y_listesi:
                ekle(f"k{kat}_{tur}_b{y:g}", tur, Pos(0, y, zb) * Rot(0, 0, -90) * parca, zb)
                ekle(f"k{kat}_{tur}_d{y:g}", tur, Pos(W, y, zb) * Rot(0, 0, 90) * parca, zb)

        orta = p.P_XY / 2
        duvar("panel", panel(),
              [orta + i * p.P_XY for i in range(nx)],
              [orta + j * p.P_XY for j in range(ny)])
        duvar("kiskac", kiskac(),
              [i * p.P_XY for i in range(1, nx)],
              [j * p.P_XY for j in range(1, ny)])
    return out
```

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `uv run pytest tests/test_montaj.py -v`
Expected: tümü PASS. Bir çakışma testi düşerse mesajdaki parça adlarından yerleşim kuralını kontrol et (döndürme yönü en olası hata).

- [ ] **Step 5: Commit**

```bash
git add src/kutu/montaj.py tests/test_montaj.py
git commit -m "Montaj: kutu(nx, ny, nz) ve çakışma kontrolü"
```

---

### Task 8: Dışa aktarma (STEP, STL, önizleme manifest'i)

**Files:**
- Create: `src/kutu/export.py`
- Test: `tests/test_export.py`

**Interfaces:**
- Consumes: `kutu()`, `Yerlesim`, parça fonksiyonları, `kilit_noktalari()`, `egimsiz_yuz_sayisi()`
- Produces:
  - `disa_aktar(cikti: Path, nx: int, ny: int, nz: int) -> dict` — manifest sözlüğünü döndürür
  - Dosyalar: `cikti/step/<tur>.step`, `cikti/stl/<tur>.stl`, `cikti/preview/<ad>.stl`, `cikti/preview/manifest.json`
  - Manifest şeması:
    ```json
    {"kutu": {"nx":1,"ny":1,"nz":1,"P_XY":200,"P_Z":100},
     "parcalar": [{"ad":"k0_kose_gb","tur":"kose","dosya":"k0_kose_gb.stl","renk":"#f39c3d","patlat":[-1,-1,0]}],
     "kilit": [{"yuz":"guney","merkez":[100,0,50]}]}
    ```
  - CLI: `uv run python -m kutu.export --nx 1 --ny 1 --nz 1 [--cikti out]`

- [ ] **Step 1: Failing test yaz**

`tests/test_export.py`:
```python
import json

from kutu.export import disa_aktar


def test_disa_aktar_tek_node(tmp_path):
    m = disa_aktar(tmp_path, 1, 1, 1)
    for tur in ("panel", "kose", "kiskac", "karo"):
        assert (tmp_path / "step" / f"{tur}.step").stat().st_size > 0
        assert (tmp_path / "stl" / f"{tur}.stl").stat().st_size > 0
    disk = json.loads((tmp_path / "preview" / "manifest.json").read_text())
    assert disk == m
    assert m["kutu"] == {"nx": 1, "ny": 1, "nz": 1, "P_XY": 200, "P_Z": 100}
    assert len(m["parcalar"]) == 10
    assert len(m["kilit"]) == 6
    for parca in m["parcalar"]:
        assert (tmp_path / "preview" / parca["dosya"]).stat().st_size > 0
        assert parca["renk"].startswith("#")
        assert len(parca["patlat"]) == 3


def test_yeniden_aktarma_eski_onizlemeyi_temizler(tmp_path):
    disa_aktar(tmp_path, 2, 1, 1)
    disa_aktar(tmp_path, 1, 1, 1)
    stl = list((tmp_path / "preview").glob("*.stl"))
    assert len(stl) == 10
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `uv run pytest tests/test_export.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kutu.export'`

- [ ] **Step 3: Dışa aktarmayı yaz**

`src/kutu/export.py`:
```python
"""STEP (kalıpçı), STL (prototip) ve önizleme (konumlu STL + manifest) çıktıları."""
import argparse
import json
from pathlib import Path

from build123d import export_step, export_stl

from kutu import params as p
from kutu.kalip import egimsiz_yuz_sayisi
from kutu.lib.kilit_yeri import kilit_noktalari
from kutu.montaj import kutu
from kutu.parts.karo import karo
from kutu.parts.kiskac import kiskac
from kutu.parts.kose import kose
from kutu.parts.panel import panel

TURLER = {"panel": panel, "kose": kose, "kiskac": kiskac, "karo": karo}
CEKME = {"panel": (0, 1, 0), "kose": (0, 0, 1), "kiskac": (0, 0, 1), "karo": (0, 0, 1)}
RENKLER = {"karo": "#5b6270", "kose": "#f39c3d", "kiskac": "#f1c40f", "panel": "#9fb3c8"}


def disa_aktar(cikti: Path, nx: int, ny: int, nz: int) -> dict:
    for alt in ("step", "stl", "preview"):
        (cikti / alt).mkdir(parents=True, exist_ok=True)

    for tur, fn in TURLER.items():
        parca = fn()
        export_step(parca, str(cikti / "step" / f"{tur}.step"))
        export_stl(parca, str(cikti / "stl" / f"{tur}.stl"))
        print(f"{tur:7s} eğimsiz yüz: {egimsiz_yuz_sayisi(parca, CEKME[tur])}")

    onizleme = cikti / "preview"
    for eski in onizleme.glob("*.stl"):
        eski.unlink()
    parcalar = []
    for y in kutu(nx, ny, nz):
        dosya = f"{y.ad}.stl"
        export_stl(y.parca, str(onizleme / dosya))
        parcalar.append({"ad": y.ad, "tur": y.tur, "dosya": dosya,
                         "renk": RENKLER[y.tur], "patlat": list(y.patlat)})

    manifest = {
        "kutu": {"nx": nx, "ny": ny, "nz": nz, "P_XY": int(p.P_XY), "P_Z": int(p.P_Z)},
        "parcalar": parcalar,
        "kilit": [{"yuz": yuz, "merkez": list(m)} for yuz, m in kilit_noktalari(nx, ny, nz)],
    }
    (onizleme / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description="Modüler kutu çıktıları")
    ap.add_argument("--nx", type=int, default=1)
    ap.add_argument("--ny", type=int, default=1)
    ap.add_argument("--nz", type=int, default=1)
    ap.add_argument("--cikti", type=Path, default=Path("out"))
    a = ap.parse_args()
    m = disa_aktar(a.cikti, a.nx, a.ny, a.nz)
    print(f"{len(m['parcalar'])} parça → {a.cikti}/preview/manifest.json")


if __name__ == "__main__":
    main()
```

> Not: `kilit_noktalari` tamsayı/float karışık döndürebilir; JSON'a `list(m)` olarak yazılır. Test manifest'i diskteki JSON ile karşılaştırdığı için tuple yerine list kullanılması şart.

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `uv run pytest tests/test_export.py -v`
Expected: tümü PASS

- [ ] **Step 5: CLI'yi çalıştır**

Run: `uv run python -m kutu.export --nx 1 --ny 1 --nz 1`
Expected: dört satır eğimsiz yüz raporu ve `10 parça → out/preview/manifest.json`

- [ ] **Step 6: Commit**

```bash
git add src/kutu/export.py tests/test_export.py
git commit -m "Dışa aktarma: STEP, STL ve önizleme manifest'i"
```

---

### Task 9: Tarayıcı önizlemesi

**Files:**
- Create: `preview/index.html`
- Modify: `.claude/launch.json` (sunucu kökü `toolbox` olur)

**Interfaces:**
- Consumes: `out/preview/manifest.json` + `out/preview/*.stl` (Task 8 şeması)

- [ ] **Step 1: launch.json'u güncelle**

`.claude/launch.json`:
```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "onizleme",
      "runtimeExecutable": "python3",
      "runtimeArgs": ["-m", "http.server", "8765", "--directory", "/Users/haandev/toolbox"],
      "port": 8765
    }
  ]
}
```

- [ ] **Step 2: Görüntüleyiciyi yaz**

`preview/index.html`:
```html
<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kutu Önizleme</title>
<style>
  html,body { margin:0; height:100%; background:#16181d; color:#e8e8ea; font:14px/1.4 system-ui,sans-serif; overflow:hidden; }
  #ui { position:absolute; top:12px; left:12px; background:#22252c; padding:12px 14px; border-radius:10px; width:240px; box-shadow:0 4px 20px #0006; }
  #ui h1 { font-size:15px; margin:0 0 6px; }
  #ui label { display:flex; align-items:center; gap:8px; margin:4px 0; cursor:pointer; }
  #ui input[type=range] { width:100%; }
  .sw { width:12px; height:12px; border-radius:3px; display:inline-block; }
  hr { border:0; border-top:1px solid #333; margin:10px 0; }
  #bilgi { color:#f39c3d; font-weight:600; }
  #hata { color:#e74c3c; }
</style>
</head>
<body>
<div id="ui">
  <h1>Modüler Kutu</h1>
  <div id="bilgi">yükleniyor…</div>
  <div id="hata"></div>
  <hr>
  <label>Patlatma <input id="patlat" type="range" min="0" max="120" value="0"></label>
  <label>Kesit (X) <input id="kesit" type="range" min="0" max="100" value="100"></label>
  <hr>
  <div id="turler"></div>
  <label><input type="checkbox" id="kilit" checked><span class="sw" style="background:#e74c3c"></span>Kilit noktaları</label>
  <label><input type="checkbox" id="izgara" checked><span class="sw" style="background:#3fa7ff"></span>Node ızgarası</label>
</div>

<script type="importmap">
{ "imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
} }
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

const KOK = '../out/preview/';
const ADLAR = { karo: 'Karo (taban/tavan)', kose: 'Köşe', kiskac: 'Kıskaç', panel: 'Panel' };

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(devicePixelRatio);
renderer.setSize(innerWidth, innerHeight);
renderer.localClippingEnabled = true;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x16181d);
const camera = new THREE.PerspectiveCamera(40, innerWidth / innerHeight, 1, 20000);
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x334455, 1.4));
const gunes = new THREE.DirectionalLight(0xffffff, 1.6);
gunes.position.set(400, -300, 800);
scene.add(gunes);

const kesitDuzlemi = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0);
const parcalar = [];   // {mesh, tur, taban: Vector3, yon: Vector3}
let kilitGrup, izgaraGrup, W, D, Hh;

function uygula() {
  const e = +document.getElementById('patlat').value;
  const gorunur = {};
  document.querySelectorAll('[data-tur]').forEach(c => gorunur[c.dataset.tur] = c.checked);
  for (const p of parcalar) {
    p.mesh.position.copy(p.yon).multiplyScalar(e);
    p.mesh.visible = gorunur[p.tur];
  }
  kilitGrup.visible = document.getElementById('kilit').checked;
  izgaraGrup.visible = document.getElementById('izgara').checked;
  kesitDuzlemi.constant = W * (+document.getElementById('kesit').value) / 100 + 0.01;
}

function izgara(m) {
  const g = new THREE.Group(), pts = [];
  const { P_XY, P_Z } = m.kutu;
  for (let x = 0; x <= W; x += P_XY) pts.push(x, 0, 0, x, D, 0, x, 0, 0, x, 0, Hh);
  for (let y = 0; y <= D; y += P_XY) pts.push(0, y, 0, W, y, 0, 0, y, 0, 0, y, Hh);
  for (let z = 0; z <= Hh; z += P_Z) pts.push(0, 0, z, W, 0, z, 0, 0, z, 0, D, z);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  g.add(new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: 0x3fa7ff, transparent: true, opacity: .4 })));
  return g;
}

async function yukle() {
  const m = await (await fetch(KOK + 'manifest.json', { cache: 'no-store' })).json();
  const { nx, ny, nz, P_XY, P_Z } = m.kutu;
  W = nx * P_XY; D = ny * P_XY; Hh = nz * P_Z;
  document.getElementById('bilgi').textContent =
    `${W / 10} × ${D / 10} × ${Hh / 10} cm · ${m.parcalar.length} parça`;

  const turler = [...new Set(m.parcalar.map(p => p.tur))];
  document.getElementById('turler').innerHTML = turler.map(t => {
    const renk = m.parcalar.find(p => p.tur === t).renk;
    return `<label><input type="checkbox" data-tur="${t}" checked><span class="sw" style="background:${renk}"></span>${ADLAR[t] ?? t}</label>`;
  }).join('');
  document.querySelectorAll('[data-tur]').forEach(c => c.onchange = uygula);

  const loader = new STLLoader();
  await Promise.all(m.parcalar.map(async p => {
    const geo = await loader.loadAsync(KOK + p.dosya);
    geo.computeVertexNormals();
    const mat = new THREE.MeshStandardMaterial({ color: p.renk, roughness: .7, clippingPlanes: [kesitDuzlemi], side: THREE.DoubleSide });
    const mesh = new THREE.Mesh(geo, mat);
    scene.add(mesh);
    parcalar.push({ mesh, tur: p.tur, yon: new THREE.Vector3(...p.patlat) });
  }));

  kilitGrup = new THREE.Group();
  const kilitMat = new THREE.MeshStandardMaterial({ color: 0xe74c3c });
  for (const k of m.kilit) {
    const s = new THREE.Mesh(new THREE.SphereGeometry(6, 16, 12), kilitMat);
    s.position.set(...k.merkez);
    kilitGrup.add(s);
  }
  scene.add(kilitGrup);
  izgaraGrup = izgara(m);
  scene.add(izgaraGrup);

  controls.target.set(W / 2, D / 2, Hh / 2);
  camera.position.set(W / 2 + 1.6 * Math.max(W, 300), D / 2 - 1.8 * Math.max(D, 300), Hh / 2 + 1.4 * Math.max(Hh, 250));
  uygula();
}

document.getElementById('patlat').oninput = uygula;
document.getElementById('kesit').oninput = uygula;
document.getElementById('kilit').onchange = uygula;
document.getElementById('izgara').onchange = uygula;
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
yukle().catch(e => {
  document.getElementById('hata').textContent =
    'Manifest yüklenemedi. Önce: uv run python -m kutu.export (' + e.message + ')';
});
(function dongu() { requestAnimationFrame(dongu); controls.update(); renderer.render(scene, camera); })();
</script>
</body>
</html>
```

- [ ] **Step 3: Tarayıcıda doğrula**

1. `uv run python -m kutu.export --nx 1 --ny 1 --nz 1`
2. `preview_start` ile `onizleme` sunucusunu başlat, `http://localhost:8765/preview/index.html` adresine git.
3. Ekran görüntüsü al. Beklenen: 20 × 20 × 10 cm · 10 parça; köşeler turuncu, paneller açık mavi, karo gri; 6 kırmızı kilit küresi her yüz merkezinde.
4. JS ile patlatmayı 60'a çek, ekran görüntüsü al: karolar yukarı/aşağı, paneller ve köşeler dışarı açılmış olmalı.
5. Kesit kaydırıcısını 50'ye çek: köşe cepleri, kuleler ve panel dilleri kesitte görünmeli.
6. `read_console_messages` ile hata olmadığını doğrula.
7. Aynısını `--nx 2 --ny 1` için tekrarla: kıskaçlar sarı, 16 parça.

- [ ] **Step 4: Commit**

```bash
git add preview/index.html .claude/launch.json
git commit -m "Tarayıcı önizlemesi (Three.js)"
```

---

### Task 10: Prototip kuponları ve spec güncellemesi

**Files:**
- Create: `src/kutu/prototip.py`
- Test: `tests/test_prototip.py`
- Modify: `docs/specs/2026-10-01-faz0-2-temel-parcalar.md` (bölüm 5.1, 7, 8, 10, 14), `docs/on-tasarim.md` (bölüm 10 Açık Sorular)

**Interfaces:**
- Consumes: `kule.kule`, `MIN3`, `params`
- Produces:
  - `kanal_kuponu(fit: float) -> Part` — 20 × 12 × 15 blok, x=10 merkezli `WALL + 2·fit` genişliğinde, üst yüzden (`y=12`) `DIL + fit` derinliğinde yarık; baskıdan sonra ayırt edilebilmesi için üst kenarda `FIT_DEGERLERI` içindeki sırası kadar (1–4) çentik
  - `dil_kuponu() -> Part` — `WALL × (DIL + 10) × 15` şerit
  - `kule_kuponu() -> Part` — 20 × 20 × WALL plaka + ortada deliği yukarı açık kule
  - `FIT_DEGERLERI = (0.1, 0.2, 0.3, 0.4)`
  - `kuponlari_aktar(cikti: Path) -> list[Path]` — `cikti/prototip/*.stl`; CLI: `uv run python -m kutu.prototip`

- [ ] **Step 1: Failing test yaz**

`tests/test_prototip.py`:
```python
import pytest
from build123d import Pos
from kutu import params as p
from kutu.prototip import (FIT_DEGERLERI, dil_kuponu, kanal_kuponu, kule_kuponu,
                           kuponlari_aktar)


@pytest.mark.parametrize("fit", FIT_DEGERLERI)
def test_kanal_kuponu_gecerli(fit):
    assert kanal_kuponu(fit).is_valid()


def test_bosluk_arttikca_hacim_azalir():
    hacim = [kanal_kuponu(f).volume for f in FIT_DEGERLERI]
    assert hacim == sorted(hacim, reverse=True)


@pytest.mark.parametrize("fit", FIT_DEGERLERI)
def test_dil_yarikta_fit_boslugu(fit):
    kanal = kanal_kuponu(fit)
    # dil yarığın ortasına, dibe fit kadar mesafeyle oturtulur
    dil = Pos(10 - p.WALL / 2, 12 - p.DIL, 0) * dil_kuponu()
    assert (kanal & dil).volume == pytest.approx(0, abs=1e-6)
    assert kanal.distance_to(dil) == pytest.approx(fit, abs=1e-3)


def test_kule_kuponu_gecerli():
    k = kule_kuponu()
    assert k.is_valid()
    assert k.bounding_box().max.Z > p.WALL


def test_kuponlari_aktar(tmp_path):
    dosyalar = kuponlari_aktar(tmp_path)
    assert len(dosyalar) == len(FIT_DEGERLERI) + 2
    for d in dosyalar:
        assert d.stat().st_size > 0
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `uv run pytest tests/test_prototip.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kutu.prototip'`

- [ ] **Step 3: Kuponları yaz**

`src/kutu/prototip.py`:
```python
"""Tolerans kalibrasyonu için küçük baskı parçaları."""
from pathlib import Path

from build123d import Box, Part, Pos, Rot, export_stl

from kutu import params as p
from kutu.lib import MIN3
from kutu.lib.kule import kule

FIT_DEGERLERI = (0.1, 0.2, 0.3, 0.4)
_BLOK = (20.0, 12.0, 15.0)
_CENTIK = 1.5


def kanal_kuponu(fit: float) -> Part:
    bx, by, bz = _BLOK
    blok = Box(bx, by, bz, align=MIN3)
    gen = p.WALL + 2 * fit
    blok -= Pos(bx / 2 - gen / 2, by - p.DIL - fit, 0) * Box(gen, p.DIL + fit, bz, align=MIN3)
    # sıra numarası kadar çentik (alt kenarda, y=0 yüzünde)
    sira = FIT_DEGERLERI.index(fit) + 1 if fit in FIT_DEGERLERI else 0
    for i in range(sira):
        blok -= Pos(1 + i * 2 * _CENTIK, 0, bz - _CENTIK) * Box(_CENTIK, _CENTIK, _CENTIK, align=MIN3)
    return blok


def dil_kuponu() -> Part:
    return Box(p.WALL, p.DIL + 10, _BLOK[2], align=MIN3)


def kule_kuponu() -> Part:
    plaka = Box(20, 20, p.WALL, align=MIN3)
    boy = p.CEP_BOY / 2
    return plaka + Pos(10, 10, p.WALL + boy) * Rot(180, 0, 0) * kule(boy)


def kuponlari_aktar(cikti: Path) -> list[Path]:
    klasor = cikti / "prototip"
    klasor.mkdir(parents=True, exist_ok=True)
    dosyalar = []
    for f in FIT_DEGERLERI:
        d = klasor / f"kanal_fit_{f:.1f}.stl"
        export_stl(kanal_kuponu(f), str(d))
        dosyalar.append(d)
    for ad, parca in (("dil", dil_kuponu()), ("kule", kule_kuponu())):
        d = klasor / f"{ad}.stl"
        export_stl(parca, str(d))
        dosyalar.append(d)
    return dosyalar


if __name__ == "__main__":
    for d in kuponlari_aktar(Path("out")):
        print(d)
```

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `uv run pytest tests/test_prototip.py -v`
Expected: tümü PASS

- [ ] **Step 5: Spec ve ön tasarımı güncelle**

`docs/specs/2026-10-01-faz0-2-temel-parcalar.md` içinde:
- Bölüm 5.1: "kenar boncuğu (~5 mm)" maddesini şu üç maddeyle değiştir: "Panel parça boyu `U + 2·DIL = 172`, yüksekliği `H + 2·DIL = 92`; diller kanal ve oluğa `DIL = 6` mm girer.", "Dil kalınlığı `WALL`; ayrı boncuk yok.", "Panel dış yüzü kanal dudağı (`LIP = 1.5`) kadar gömük."
- Bölüm 7: "`out/glb/` + `out/manifest.json`" maddesini "`out/preview/` — konumlu STL'ler + `manifest.json` (önizleme)" ile değiştir.
- Bölüm 10: yolu `src/kutu/prototip.py` → `out/prototip/` olarak düzelt.
- Bölüm 14'e ekle: "6. **Kalıp eğimi:** Bu fazda geometriye uygulanmadı; `kalip.py` eğimsiz yüzleri raporluyor. Kalıp hazırlık fazında uygulanacak.", "7. **Karo çerçevesi kalın kesit:** Kenar çerçevesi K × T dolu; çökme izi (sink) riski. Kalıp hazırlıkta alttan oyulacak."

`docs/on-tasarim.md` bölüm 10'da: 1, 2, 3, 6 numaralı soruların sonuna "→ Çözüldü, bkz. `docs/specs/2026-10-01-faz0-2-temel-parcalar.md`" ekle; 5 numaraya "→ Karo (200×200, taban=tavan); çok node'lu tabanlar karo birleşimi." ekle.

- [ ] **Step 6: Tüm testleri koş ve çıktıları üret**

Run: `uv run pytest -v && uv run python -m kutu.export && uv run python -m kutu.prototip`
Expected: tüm testler PASS; `out/step`, `out/stl`, `out/preview`, `out/prototip` dolu.

- [ ] **Step 7: Commit**

```bash
git add src/kutu/prototip.py tests/test_prototip.py docs/
git commit -m "Prototip tolerans kuponları; spec ve ön tasarım güncellendi"
```
