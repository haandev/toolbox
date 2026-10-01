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

## 4. Node, ızgara ve kilit noktası kuralı

- Sistemin temel birimi **node**: 200 × 200 × 100 mm. En küçük kutu (20×20×10) tek bir node'dur.
- Her kutu, node'ların X, Y ve Z yönünde birleşimidir: `kutu(nx, ny, nz)` (ör. 40×40×20 = 2×2×2 node).
- Kutunun dış ölçüsü daima node'un tam katıdır.
- **Kilit noktaları:** Her dikey yüzde her node yüzünün (200×100) merkezi (`x = 100 + 200k`, `z = 50 + 100j`); alt ve üst yüzde her node yüzünün (200×200) merkezi.
- Bu kural kutu boyutundan, kaydırmadan ve döndürmeden bağımsız olarak kilit noktalarının çakışmasını garanti eder.
- Bu spec'te kilit geometrisi **tasarlanmaz**; her kilit noktasında boş bir **kilit bölgesi** hacmi ayrılır (`lib/kilit_yeri.py`).

## 5. Parçalar

### 5.1 Duvar paneli — 160 × 80
- Dış yüz: 2.5 mm düz deri. İç yüz: 1.5 mm kaburga ızgarası.
- Merkezde ~60 × 50 mm kilit bölgesi; kaburgalar bu bölgenin yükünü kenarlara taşır.
- Panel parça boyu `U + 2·DIL = 172`, yüksekliği `H + 2·DIL = 92`; dört kenardaki diller kanal ve oluğa `DIL = 6` mm girer (kesit `lib/kanal.py`).
- Dil kalınlığı `WALL`; ayrı boncuk yok (panel her yönden sarıldığı için gerekmedi).
- Panel dış yüzü kanal dudağı (`LIP = 1.5`) kadar gömük; dudak olmadan panel dışarı düşer.
- Alt ve üst kenarda dil; karo oluğuna oturur.
- Kalıp çekiliş yönü: panel yüzüne dik. Ayrım çizgisi boncuk ortasından; undercut yok.
- Vidasız; kanal ve oluklar tarafından tutulur.

### 5.1a Hata önleyici anahtar
> **Değişti:** Bu bölüm `docs/specs/2026-10-01-kayar-duvar.md` ile değiştirildi (kayar duvar). Önceki hal git etiketi `dikey-centik`'te.

Panel baş aşağı ya da içi dışına takılırsa yan kilit dil–oluğu yer değiştirir ve kutular kilitlenmez. Panel simetrik yapılamaz (boydan boya dil–oluk 180° çevrilince birbirinin yerine geçer), bu yüzden tek bir anahtar kullanılır:
- Panelin **yalnız alt dilinde**, merkezden `ANAHTAR_X = +40` mm'de, içe doğru `ANAHTAR_T = 2` mm çıkıntı (`ANAHTAR_W = 10`).
- **Taban** oluğunda ve **yatay kıskacın üst** oluğunda karşılık gelen cep; tavan ve yatay kıskacın alt oluğunda cep yok.
- Baş aşağı takılan panelin anahtarı üste geçer, tavan kapanmaz; içi dışına takılanın anahtarı dışa geçer, taban oluğunun dış dudağına çarpar.

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

### 5.4a Dikey istif ve tavan (tek parça, gömme kulplu)
> **Değişti:** Bu bölüm `docs/specs/2026-10-01-kayar-duvar.md` ile değiştirildi (kayar duvar). Önceki hal git etiketi `dikey-centik`'te.

Dikeyde her zaman alttaki kutunun tavanı üstteki kutunun tabanıyla buluşur; cinsiyetsizlik yalnızca
**yan yüzlerde** gerekir. Dikeyde erkek–dişi oturma kullanılır.
- **Taban:** node karoları (modüler). Alt cep dişi yuvadır; kaburga uçları tutucu bandında `ERKEK_H + FIT` kısaltılır.
- **Tavan:** kutu boyuna göre **tek parça** (`tavan(nx, ny)`: 1×1, 2×1, 3×1, 2×2 …). Her node'un 4 köşesinde **L tutucu** kilit yüzünden `ERKEK_H = 5` mm taşar ve üstteki tabanın dişi yuvasına `FIT` ile oturur.
- **Gömme kulp:** 1×, 2×, 3× (kutunun x'teki node sayısı, en çok 3). Kutunun tam ortasında; tavanın içinde, **kilit yüzünün altındaki** oyukta katlı yatar. Oyuk kutunun içine `WALL` kabuklu bir tekne olarak sarkar (~15 mm). Mafsal ekseni kulp boyunca; açılınca tutma yeri merkezden `KULP_KOL = 40` mm kayık.
- Kulp istif arayüzüne girmediği için üstteki kutu (karo tabanı ve ek yerleriyle) her boyutta çakışmadan oturur (1×1, 2×1, 3×1, 2×2 testli).
- L tutucular tam bilezik yerine seçildi: kulp açılırken süpürdüğü bölge tutucu kollarından kırpılır.
- **Neden tavan karo değil:** Karo tavan + istif arayüzüne gömülü kulp, üstteki kutunun karo tabanındaki ek yeri çerçeveleriyle çakışıyor (modelde 4693 mm³). Tavanı tek parça yapmak bunu çözüyor; bedeli kutu boyu başına bir tavan kalıbı.
- Dikey çekme kilidi (üstteki kutudan tutunca alttakinin de kalkması) ayrı bir mandal ister; sıradaki iş.

### 5.4d Dikey çekme mandalı
> **Değişti:** Bu bölüm `docs/specs/2026-10-01-kayar-duvar.md` ile değiştirildi (kayar duvar). Önceki hal git etiketi `dikey-centik`'te.

Erkek–dişi oturma kutuları hizalar ama birbirine bağlamaz; üstteki kutudan tutunca alttakinin de kalkması için mandal.
- Dış yüzde yer yok (panel dış yüzü ile kutu yüzü arası 1.5 mm; dışa taşan mandal komşu kutuya çarpar), bu yüzden **kayar kanca**:
- **Tavanda:** kenar çerçevesinin iç kısmında (y 7–17 mm) sürgü cebi. Sürgüden yukarı çıkan kanca kilit yüzünü geçer. Sürgüye bağlı dil, panel oluğunun üstünden kutu yüzüne uzanır; dışarıdan parmakla itilir (`MANDAL_YOL = 10` mm).
- **Taban karosunda:** her kenarda anahtar deliği biçimli yuva (giriş penceresi + oda); oda tabanı ile pencere arasındaki çerçeve malzemesi tutma çıkıntısıdır. Dört kenarda olduğu için üstteki kutu 90°/180° döndürülse de mandala denk gelir.
- Konum: ön ve arka yüzde, her node'da bir mandal (node kenar ortasından `MANDAL_X = −35` mm; yan kilit oluğu ve anahtar cebiyle çakışmaz).
- Kilitliyken kanca başı çıkıntının `FIT` üstünde; üstteki kutu 1 mm kalkınca takılır (testli). Açıkken serbest kalkar.
- Açık konuda: sürgünün yaylı tutucusu (kendiliğinden açılmasın diye detent) ve dilin parmak girintisi henüz modellenmedi.

### 5.4e Çekmece ve raf
- `kutu(..., cekmece=True)`: ön (güney) yüzde panel yerine her node ve her kat için bir çekmece. Gövdenin geri kalanı aynı modüler parçalar.
- **Çekmece:** ön plaka panel dış yüzüyle aynı hizada, köşe/kıskaç arasında `CEKMECE_B = 0.5` yan boşlukla; üst ortada 60×15 parmak girintisi. Arkasında `WALL` kalınlığında tepsi, arka panel kaburgalarının `FIT` önünde biter. Tabanın (ya da rafın) üstünde `FIT` boşlukla kayar; köşeler ve kıskaçlar yanlardan hizalar.
- Tepsi yüksekliği: alt katlarda yatay kıskacın altına, en üst katta tavanın kulp teknesinin (`TEKNE_ALT = 17` mm) altına kadar.
- **Raf (2H ve üstü):** kat arasında yatay kıskaçların iç çıkıntılarına oturan `WALL` kalınlığında plaka; üst kat panel kaburgalarının içinde kalır (`RAF_KENAR`), köşe ve kıskaç izlerinde çentikli. Kutu boyuna göre tek parça.
- Ön yüzdeki yatay kıskaç kalır; çekmeceler arasında ayırıcıdır.
- Testli: kapalıyken çakışma yok (1×1, 2×1, 1×1×2, 2×1×2), çekmece 180 mm'ye kadar çekilirken yolu açık, üst çekmece rafa `FIT` ile oturur, raf yatay kıskaçlara değer.
- **Durdurucu (kaldır-çıkar):** taban karosunun çerçevesi üstünde her kenar ortasında 8×4×2 mm çıkıntı (tek kalıp; tepsinin dışında kalır), üst katlarda rafın üstünde. Tepsi altındaki önden açık oluğun içinde kayar; oluk bitince çekmece `CEKMECE_YOL = 120` mm'de durur. Takıp çıkarmak için çekmecenin önü kaldırılır; esnek parça yok.
- **Kapalı tutucu:** oluk tavanında, kapalıyken çıkıntının hemen önünde 0.6 mm tümsek; çıkıntı tümseği aşmadan çekmece açılmaz (1 mm'de direnç, 10 mm'de serbest — testli).
- **Raf sehimi:** raf altında 18 mm derin kaburga ızgarası (yatay kıskaçların iç yüzünden içeride, alt çekmecenin 2 mm üstünde). 5 kg yayılı yükte hesaplanan sehim: 1×1 0.17 mm, 2×1 0.07 mm, 3×1 0.05 mm, 2×2 0.84 mm (kaburgasız 2.5 mm plaka: 2.8–49 mm). Model: kısa açıklık boyunca basit mesnetli T kesitli kaburgalar, PP E = 1.3 GPa (`raf_sehimi()`).

### 5.4c Yan kilit (deneme — `YAN_KILIT`)
> **Değişti:** Bu bölüm `docs/specs/2026-10-01-kayar-duvar.md` ile değiştirildi (kayar duvar). Önceki hal git etiketi `dikey-centik`'te.

Dikey istif kutuları zaten kilitlediği için yan kilit isteğe bağlıdır; `YAN_KILIT = False` ile tamamen kalkar.
- Yatay pim kullanılamaz: kutu komşusunun yanına yukarıdan indirilir (alttaki tavana oturmak için), yandan taşan pim bunu engeller.
- Panel kilit bölgesinde dış yüze ped; ped üzerinde **dikey dil** (−x, `YAN_KILIT_X = 15`) ve **dikey oluk** (+x). 180° çevrilen komşunun dili bu oluğa denk gelir (cinsiyetsiz).
- Oluk **boydan boya açık**: panel, yatay kıskaç, taban ve tavanda aynı hizada çentik var. Böylece 2H kutu üst üste iki 1H kutunun yanına indirilirken dil hiçbir katta takılmaz; durdurucu yok, yüksekliği dikey istif belirler.
- Düz kesit (kırlangıç değil): kalıpta sürgü gerektirmez; görevi yalnızca kayma ve hizalama.
- Dil kutu yüzünden `YAN_DIL_H − GAP = 2.5` mm taşar; tek başına duran kutunun ayak izi her yanda bu kadar büyür.

### 5.4b Kat arası bağlantı (nz > 1)
Kat aralarında karo çifti (ara raf) yok; bunun yerine yatayda kullanılan mantık dikeyde tekrarlanır:
- **Yatay kıskaç** — 160 × 20 × 20 profil (2T yüksekliğinde). Altta ve üstte panel oluğu; iki uçta düğüm kanalına giren dil. Dil, kanal içinde alt ve üst panel dillerinin arasına `FIT` boşlukla oturur. İçten oyuk, kaburgalı; çekiliş yönü +y.
- **Köşe düğümü** — köşe kesitinin 20 mm boyu; kule yerine vida geçiş deliği.
- **Kıskaç düğümü** — kıskaç kesitinin 20 mm boyu; iki vida geçiş deliği.
- Köşe ve dikey kıskaç her yükseklikte 80 mm kalır; her kutu yüksekliği aynı parçalardan kurulur (yeni kalıp yok).
- Parça sayısı: panel, köşe, kıskaç, taban, yatay kıskaç, köşe düğümü, kıskaç düğümü (7 modüler parça) + boya göre tavan ve 1×/2×/3× kulp.

### 5.5 Kurulum sırası
1. Köşe ve kıskaçlar tabana oturur.
2. Paneller kanallara yukarıdan kayar.
3. Tavan kapanır.
4. Her köşe ve kıskaca altta ve üstte birer vida.

### 5.6 Rijitlik
Rijitliğin ana kaynağı, panellerin dört kenardan sıkıştığı alt ve üst plakalardır; köşe tek başına yamulmayı engellemek zorunda değildir.

## 6. Montaj (`src/kutu/montaj.py`)

`kutu(nx, ny, nz)` tüm parçaları konumlarıyla döndürür. Bu spec'te yalnızca `kutu(1, 1, 1)` kabul kriteridir; `nx, ny > 1` yalnızca ızgara testi için üretilir (ortadaki karo ek yeri çözülmeden).

2H ve üstü kutular (nz > 1) kat aralarında yatay kıskaç ve düğümlerle kurulur (bkz. 5.4b); taban ve tavan yalnızca en alt ve en üstte.

## 7. Çıktılar (`src/kutu/export.py`)

- `out/step/` — kalıpçı için STEP (her parça tipi).
- `out/stl/` — prototip baskı için STL.
- `out/preview/` — konumlu STL'ler + `manifest.json` (parça adı, tür, renk, patlatma yönü, kilit noktaları).
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

## 10. Prototip parçaları (`src/kutu/prototip.py` → `out/prototip/`)

- Boncuk–kanal test kuponu, `FIT` ∈ {0.1, 0.2, 0.3, 0.4}.
- Insert kulesi test parçası.
- Kullanıcı basar; sonuç `FIT` değerine işlenir.

## 11. Repo yapısı

```
toolbox/
├── pyproject.toml
├── docs/
├── src/kutu/{params.py, kalip.py, lib/, parts/, montaj.py, export.py, prototip.py}
├── tests/
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
6. **Kalıp eğimi:** Bu fazda geometriye uygulanmadı; `kalip.py` eğimsiz yüzleri raporluyor (panel 44, köşe 20, kıskaç 20, karo 104). Kalıp hazırlık fazında uygulanacak.
7. **Karo çerçevesi kalın kesit:** Kenar çerçevesi K × T dolu; çökme izi (sink) riski. Kalıp hazırlıkta alttan oyulacak.
8. **Düğüm vida bağlantısı:** Alttaki köşenin üst kulesi ve üstteki köşenin alt kulesi düğüme bakıyor; ikisini düğümden geçen tek bir saplama/uzun vida ile bağlamak öngörülüyor. Detay kalıp hazırlıkta netleşecek.
