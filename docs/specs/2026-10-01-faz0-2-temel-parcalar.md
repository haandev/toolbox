# Spec: Faz 0–2 — Temel Parçalar ve İlk Kutu

Tarih: 2026-10-01
Kaynak: `docs/on-tasarim.md` (bu spec, ön tasarımın aşağıda belirtilen kararlarını değiştirir)

## 1. Amaç ve bağlam

Modüler kutu sisteminin ilk dört parça tipini (panel, kıskaç, köşe, karo) ve bunlardan kurulan 20×20×10 cm kutuyu parametrik olarak tasarlamak.

Nihai hedef **endüstriyel enjeksiyon kalıplama ile seri üretim** ve ürün olarak satış. 3D baskı yalnızca prototip içindir. Bu yüzden geometri baştan kalıplanabilir tasarlanır.

## 2. Ön tasarımdan değişen kararlar

| Konu | Ön tasarım | Bu spec |
|---|---|---|
| Üretim | 3D baskı | Enjeksiyon kalıplama; baskı yalnızca prototip |
| CAD aracı | OpenSCAD | build123d (Python); STEP + STL + GLB çıktısı |
| Bağlantı | Vida + heat-set insert | Karma: paneller geçmeli, köşe/kıskaç uçlarında vida. Seri üretimde plastiğe uygun vida + kalıptan çıkan kule; prototipte insert (`PROTO` bayrağı) |
| Dış ölçü | `n×160 + 40` (1→200, 2→360) | Izgara adımı: yatayda 200, dikeyde 100 mm (1→200, 2→400) |
| Kutu-kutu kilit yeri | Kıskacın dış yüzü | Her yüzde, her hücrenin merkezi (panel merkezleri, karo merkezleri) |
| Taban / tavan | Ayrı parçalar | Tek parça (karo), tavan olarak ters çevrilir |
| Sap yuvası | Tavanda özel yuva | Yok; sap, kilit arayüzüne takılan bir aksesuar |
| Baskı kısıtları | Desteksiz, tabla boyutu | Öncelik değil; kalıp kuralları geçerli |

## 3. Parametreler (`src/kutu/params.py`)

Tüm ölçüler bu dosyadan gelir; parça dosyalarında sabit sayı yazılmaz.

### 3.1 Izgara (girdi)
| Ad | Değer | Anlam |
|---|---|---|
| `P_XY` | 200 | Yatay ızgara adımı |
| `P_Z` | 100 | Dikey ızgara adımı |
| `U` | 160 | Panel genişliği |
| `H` | 80 | Panel yüksekliği |
| `GAP` | 0.5 | Komşu kutular arası taraf başı boşluk |

### 3.2 Türetilen (elle değiştirilmez)
- `K = (P_XY − U) / 2 = 20` — köşe katkısı; kıskaç genişliği `2K = 40`.
- `T = (P_Z − H) / 2 = 10` — karo kalınlığı / katkısı.
- Kutu gerçek dış ölçüsü: `n × P_XY − 2·GAP` (yatay), `m × P_Z − 2·GAP` (dikey).
- Izgara eşitlikleri: `2K + n·U + (n−1)·2K = n·P_XY` ve `2T + m·H + (m−1)·2T = m·P_Z`.

### 3.3 Kalıp kuralları
| Ad | Değer |
|---|---|
| `WALL` | 2.5 mm |
| `RIB` | 0.6 × WALL = 1.5 mm |
| `DRAFT_OUT` | 1.5° |
| `DRAFT_IN` | 1.0° |
| `R_IN_MIN` | 0.5 × WALL |
| `FIT` | 0.2 mm (prototiple kalibre edilecek) |

### 3.4 Vida
- Tek vida boyu: plastiğe uygun 4 mm vida (Delta PT / KA tipi).
- Kule: iç delik ~3.2 mm, dış ~8.5 mm, kökte kaburga desteği.
- `PROTO = True` iken kule deliği heat-set insert ölçüsüne döner.

### 3.5 Malzeme varsayımı
Kopolimer PP. Yalnızca klips esneme hesabını etkiler; tek parametre ile değişir.

## 4. Izgara ve kilit noktası kuralı

- Kutular 200 × 200 × 100 mm hücrelerden oluşur.
- **Kilit noktaları:** Her dikey yüzde her 200×100 hücrenin merkezi (`x = 100 + 200k`, `z = 50 + 100j`); alt ve üst yüzde her 200×200 hücrenin merkezi.
- Bu kural kutu boyutundan, kaydırmadan ve döndürmeden bağımsız olarak kilit noktalarının çakışmasını garanti eder.
- Bu spec'te kilit geometrisi **tasarlanmaz**; her kilit noktasında boş bir **kilit bölgesi** hacmi ayrılır (`lib/kilit_yeri.py`).

## 5. Parçalar

### 5.1 Duvar paneli — 160 × 80
- Dış yüz: 2.5 mm düz deri. İç yüz: 1.5 mm kaburga ızgarası.
- Merkezde ~60 × 50 mm kilit bölgesi; kaburgalar bu bölgenin yükünü kenarlara taşır.
- Yan kenarlarda kenar boncuğu (~5 mm, profil `lib/kanal.py`'den); kıskaç/köşe kanalına yukarıdan kayar.
- Alt ve üst kenarda dil; karo oluğuna oturur.
- Kalıp çekiliş yönü: panel yüzüne dik. Ayrım çizgisi boncuk ortasından; undercut yok.
- Vidasız; kanal ve oluklar tarafından tutulur.

### 5.2 Kıskaç — 40 × 80, dikey profil
- İki yanında panel kanalı. İçi oyuk, kaburgalı.
- Alt ve üst uçta birer vida kulesi.
- Çekiliş yönü dikey.
- Dış yüz düz, panel dış yüzüyle aynı hizada. Kilit taşımaz.

### 5.3 Köşe — 20 × 20 × 80, dikey profil
- İçe bakan iki yüzde 90° panel kanalı. Dış köşe R5.
- İçi oyuk, kaburgalı; alt ve üst uçta vida kulesi.
- Çekiliş yönü dikey.

### 5.4 Karo — 200 × 200 × 10 (taban = tavan)
- Bir yüz: panel çevre oluğu, köşe ve kıskaç yuvaları, vida delikleri.
- Diğer yüz: hücre merkezinde kilit bölgesi, kenarda yürüme halkası.
- Taban: oluk yukarı. Tavan: aynı parça ters çevrilmiş, oluk aşağı.
- Çok hücreli kutularda karolar yan yana birleşir. Kenar ek yerleri kıskaç altına düşer; kıskaç vidası iki karo kenarını birlikte tutar.

### 5.5 Kurulum sırası
1. Köşe ve kıskaçlar tabana oturur.
2. Paneller kanallara yukarıdan kayar.
3. Tavan kapanır.
4. Her köşe ve kıskaca altta ve üstte birer vida.

### 5.6 Rijitlik
Rijitliğin ana kaynağı, panellerin dört kenardan sıkıştığı alt ve üst plakalardır; köşe tek başına yamulmayı engellemek zorunda değildir.

## 6. Montaj (`src/kutu/montaj.py`)

`kutu(nx, ny, nz)` tüm parçaları konumlarıyla döndürür. Bu spec'te yalnızca `kutu(1, 1, 1)` kabul kriteridir; `nx, ny > 1` yalnızca ızgara testi için üretilir (ortadaki karo ek yeri çözülmeden).

2H kutular (nz = 2) geçici olarak sırt sırta iki karo ile kurulur (10 + 10 = 20 mm). Ara bilezik parçası Faz 6'da değerlendirilir.

## 7. Çıktılar (`src/kutu/export.py`)

- `out/step/` — kalıpçı için STEP (her parça tipi).
- `out/stl/` — prototip baskı için STL.
- `out/glb/` + `out/manifest.json` — önizleme için (parça adı, renk, konum, patlatma vektörü).
- `out/` git'e girmez.

## 8. Önizleme (`preview/index.html`)

Three.js tabanlı, uygulamanın tarayıcı panelinde açılır. Özellikler:
- Parça aç/kapat
- Patlatılmış görünüm
- Izgara (200/100) ve kilit noktası gösterimi
- Kesit düzlemi

## 9. Testler (`tests/`, pytest)

- **Izgara:** 3.2'deki eşitlikler; kilit noktalarının hücre merkezlerinde olması.
- **Parça:** geçerli katı; kutu ölçüleri; duvar ve kaburga kalınlığı kurala uygun.
- **Montaj:** parçalar arası kesişim hacmi ≈ 0; boncuk–kanal arası `FIT` boşluğu.
- **Kalıp eğimi (deneysel, uyarı):** çekiliş yönüne paralel yüzlerde eğim kontrolü.

## 10. Prototip parçaları (`prototip/`)

- Boncuk–kanal test kuponu, `FIT` ∈ {0.1, 0.2, 0.3, 0.4}.
- Insert kulesi test parçası.
- Kullanıcı basar; sonuç `FIT` değerine işlenir.

## 11. Repo yapısı

```
toolbox/
├── pyproject.toml
├── docs/
├── src/kutu/{params.py, lib/, parts/, montaj.py, export.py}
├── tests/
├── prototip/
├── preview/index.html
└── out/        (gitignore)
```

## 12. Bitiş kriteri

1. 20×20×10 kutu görüntüleyicide kurulu ve patlatılabilir.
2. Dört parçanın STEP ve STL'si üretiliyor.
3. Tüm testler geçiyor.
4. Prototip parçalarının STL'leri hazır.

## 13. Kapsam dışı

- Cinsiyetsiz kilit geometrisi (ayrı spec)
- Sap, çekmece, kapak, iç bölmeler
- Dört karonun buluştuğu iç ek yeri (Faz 6)
- Kalıp akış analizi, büzülme payı (kalıpçı uygular)

## 14. Açık riskler ve sorular

1. **Karo iç ek yeri:** 40×40 ve üstünde dört karonun buluştuğu noktanın üstünde duvar yok; bindirme + vida ile çözülmesi öngörülüyor, Faz 6'da doğrulanacak.
2. **Kilit bölgesi ölçüsü:** 60×50 mm varsayım; kilit spec'inde kesinleşecek.
3. **Malzeme:** PP varsayımı; yük kapasitesi hedefi (kutu başına kg) henüz yok.
4. **Gridfinity uyumu:** 1 hücre iç ölçüsü ~190 mm; 4×42 = 168 mm sığar ama boşluk kalır. Karar ertelendi.
5. **Lisans / ticari koruma:** Ürün satışı hedeflendiği için açık lisans yerine tasarım tescili değerlendirilebilir; karar ertelendi.
