# Kayar Duvar — Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Yan kilidi yatay raya çevirmek, dikey istifi öne kayabilir yapmak (kılavuz ray + T kanal), böylece kutulardan kurulan duvarda her kutu çekmece gibi çıkarılabilsin.

**Architecture:** Yeni ortak modül `lib/yan_ray.py` ray şeridi/dil/oluk geometrisini panel çerçevesinde üretir; panel, köşe ve kıskaç bunu kullanır. Montaj batı ve kuzey panellerini baş aşağı yerleştirir. Tavan L tutucular ve kayar mandal yerine kılavuz ray + T kanca; taban karosu kılavuz çentiği + T kanal. Eski dikey yan kilit kodu kaldırılır.

**Tech Stack:** Python 3.12, build123d 0.13, pytest, Three.js önizleme.

**Spec:** `docs/specs/2026-10-01-kayar-duvar.md`

## Global Constraints

- Tüm ölçüler `params.py`'de; parça dosyalarında sabit sayı yok.
- `RAY_D = 20`, `RAY_H = 8`, `RAY_T = 3`, `KILAVUZ_H = 3`; T kanal: boyun `z = GAP … 1.6`, baş `z = 1.6 … 3.0`.
- Panel yön kuralı: doğu/güney normal, batı/kuzey baş aşağı (`Pos(0,0,P_Z/2)·Rot(0,180,0)·Pos(0,0,−P_Z/2)`, kat içinde).
- Geri dönüş noktası: git etiketi `dikey-centik`.
- Mevcut kulp, çekmece, istif testleri geçmeye devam eder (çekmece/kulp davranışı değişmez).

## Review Focus

1. **Çok node'lu kutunun yanında kayma:** dil ray, komşunun kıskaç izinden geçmeli → Task 3/7'de 2×1 kutu yanında 1×1 kaydırma testi.
2. **2H kutu duvarda:** iki kattaki raylar ve yatay kıskaç bandı; 2H kutunun yanında iki 1H kutu → Task 7 testi.
3. **Kulp açılırken kılavuz raylar:** süpürme zarfı daraltıldıktan sonra kulp açık testi → Task 5.
4. **Çekmeceli kutu duvarda:** ön panel yok, batı/kuzey kuralı çekmeceyi etkilememeli → mevcut çekmece testleri + Task 7'de çekmeceli kutu içeren duvar.
5. **Kayarak takma sırasında T kancanın taban kaburgalarına çarpması:** kaburga şeritleri → Task 6 kaydırma testi.

---

### Task 1: Ray parametreleri ve `lib/yan_ray.py`

**Files:** Modify `src/kutu/params.py`; Create `src/kutu/lib/yan_ray.py`; Test `tests/test_yan_ray.py`

**Interfaces — Produces:**
- `params.RAY_D, RAY_H, RAY_T, RAY_V1(kat tabanından), RAY_V2`
- `yan_ray.serit(u0, u1) -> Part` — panel çerçevesinde iki yükseklikteki şeritler (`y = GAP … GAP+LIP`)
- `yan_ray.dil(u0, u1) -> Part` — `v₁`'de, `y = GAP−RAY_T … GAP`
- `yan_ray.oluk(u0, u1, derin) -> Part` — `v₂`'de kesim hacmi (`y = GAP−0.01 … GAP+derin`)
- `yan_ray.dis_oluklar(u0, u1, yuz_y) -> Part` — her iki yükseklikte, dış yüzü `yuz_y` olan profile (köşe/kıskaç) komşu dilinin geçeceği oluk

- [ ] Test: v₁/v₂ simetrik (`v₁ + v₂ = 2·(T + H/2)`), dil kesiti `RAY_T × RAY_H`, oluk dil+FIT'i sarar.
- [ ] Kod, testi geçir, commit.

### Task 2: Panel yatay raylar

**Files:** Modify `src/kutu/parts/panel.py`, `tests/test_panel.py`; Replace `tests/test_yan_kilit.py`

- [ ] Test: `YAN_KILIT=True` iken panel `min.Y = GAP − RAY_T`; `v₁`'de dil var, `v₂`'de oluk boş (görünür açıklık boyunca); oluk arkasında destek şeridi; `YAN_KILIT=False` iken eski davranış.
- [ ] Panel: `_yan_kilit` → şerit + dil − oluk + destek; eski ped/dikey dil/oluk kaldırılır.
- [ ] Commit.

### Task 3: Köşe ve kıskaç dış oluklar

**Files:** Modify `src/kutu/parts/kose.py`, `src/kutu/parts/kiskac.py`; Tests `tests/test_yan_kilit.py`

- [ ] Test: köşenin iki dış yüzünde ve kıskacın dış yüzünde `v₁` ve `v₂`'de oluk boş.
- [ ] Kod: `_profil` sonrası `dis_oluklar` çıkarılır (köşede güney yüzü + 90° döndürülmüş batı yüzü). Commit.

### Task 4: Montaj yön kuralı, eski dikey çentiklerin kaldırılması, anahtar cepleri

**Files:** Modify `src/kutu/montaj.py`, `src/kutu/parts/{karo,tavan,yatay_kiskac}.py`, `src/kutu/lib/kilit_yeri.py`; Tests `tests/test_anahtar.py`, `tests/test_yan_kilit.py`

- [ ] Test (yan_kilit): 1×1 yanında 1×1 (x komşu) ve arkasında 1×1 (y komşu) çakışmaz, paneller arası mesafe `FIT`; 2×1 yanında 1×1 çakışmaz.
- [ ] Test (anahtar): doğu panel baş aşağı → tavana çarpar; batı panel montajdaki hali (baş aşağı) çakışmaz; içi dışına → çarpar.
- [ ] Montaj: batı/kuzey panel ve yatay kıskaç baş aşağı yerleşim; taban/tavan/yatay kıskaçtaki `yan_oluk` çentikleri kaldırılır; tavan batı/kuzey kenarına `u=−40` anahtar cebi; yatay kıskaç alt oluğuna `u=−40` cep.
- [ ] Tüm testleri koş, commit.

### Task 5: Kılavuz raylar (L tutucular yerine)

**Files:** Modify `src/kutu/parts/tavan.py`, `src/kutu/parts/karo.py`, `src/kutu/params.py`; Tests `tests/test_taban_tavan.py`, `tests/test_tavan_kulp.py`

- [ ] Test: tavan node başına iki kılavuz ray (y boyunca tam), yükseklik `KILAVUZ_H`; taban dört kenarda kılavuz çentiği (z ≤ KILAVUZ_H+FIT) boş; istifte FIT hizalama; üst kutu −y'de 0…P_XY kaydırılırken kılavuzlar çakışmaz.
- [ ] Kod: `_kose_tutuculari` → `_kilavuzlar`; `ERKEK_H` → `KILAVUZ_H`; süpürme zarfı x'i kollara daraltılır; taban çentikleri. Commit.

### Task 6: T kanal (mandal yerine)

**Files:** Create `src/kutu/parts/t_kanal.py`; Modify `tavan.py`, `karo.py`, `montaj.py`, `export.py`; Delete `src/kutu/parts/mandal.py`, `tests/test_mandal.py`; Test `tests/test_t_kanal.py`

- [ ] Test: tavanda node başına ön+arka T kanca; tabanda dört kenarda T kanal boş (boyun+baş), kanca şeritlerinde kaburga kırpık; istifte çakışma yok; üst kutu +1 mm → çarpar (dikey kilit); üst kutu −y kaydırılınca çakışmaz (kayarak takma/çıkarma).
- [ ] Kod; montajdan `mandal` seçeneği kaldırılır (export dahil). Commit.

### Task 7: Duvar testleri ve önizleme

**Files:** Create `tests/test_duvar.py`; Modify `src/kutu/export.py`, `preview/index.html`

- [ ] `duvar(sutun, kat)` test yardımcısı: 1×1 kutulardan duvar.
- [ ] Testler: 2×2 ve 3×2 duvar çakışmasız; alt orta kutu −y'de 0…200 kayarken çakışmaz; alt kutu kaldırılınca üstteki 1 mm aşağıda komşu raya çarpar; 2H kutu yanında iki 1H; çekmeceli kutu içeren duvar.
- [ ] `export --duvar` sahnesi (3×2, alt orta yarı çekili). Commit.

### Task 8: Belgeler

- [ ] Eski spec'te 5.1a, 5.4a, 5.4c, 5.4d bölümlerine "kayar duvar spec'i ile değişti" notu; kayar duvar spec'ine uygulama notları. Commit, `master`'a birleştir.
