# Spec: Kayar Duvar — her kutu komşusunun rayı

Tarih: 2026-10-01
Önceki spec: `docs/specs/2026-10-01-faz0-2-temel-parcalar.md` (bu spec onun 5.1a, 5.4a, 5.4c, 5.4d bölümlerini değiştirir)

## 1. Amaç

Kutulardan kurulan bir duvarda (yan yana ve üst üste) **herhangi bir kutu çekmece gibi öne kayarak çıkabilsin**, üstündeki kutular düşmesin. Ayrı bir dolap ya da çerçeve olmadan: **her kutu, yanındaki kutu için ray görevi görür.**

## 2. Temel fikir

- Yan yüzlerdeki kilit **yatay** olur: panelde ön-arka boyunca uzanan bir **dil ray** ve bir **oluk ray**. Komşu kutunun dili bu oluğa girer.
- Bir kutunun altındaki kutu çekildiğinde, kutu yan komşularının raylarında asılı kalır.
- Dikey istif arayüzü (tavan–taban) **öne kaymaya izin verir**; dikeyde kilit, önü açık **T kanal** ile sağlanır.

## 3. Yan raylar

### 3.1 Panel
- Panel kilit bölgesindeki eski ped ve dikey dil–oluk kaldırılır.
- Panelin dış yüzünde, görünür açıklık boyunca (`u ∈ [−U/2, U/2]`) iki yatay **ray şeridi**: şerit, panelin gömük yüzünü kutu yüzüne kadar doldurur (`y = GAP … GAP+LIP`).
  - **Dil ray:** `v₁ = T + H/2 − RAY_D` yüksekliğinde, şeritten `RAY_T = 3` mm dışarı taşan, `RAY_H = 8` mm yüksekliğinde düz kesitli ray.
  - **Oluk ray:** `v₂ = T + H/2 + RAY_D` yüksekliğinde, `RAY_H + 2·FIT` genişliğinde, `RAY_T + FIT` derinliğinde oluk; arkasında deriyi destekleyen `WALL` kalınlığında iç şerit.
- `RAY_D = 20` mm: `v₁ = 30`, `v₂ = 70` (kat tabanından).
- `v₁` ve `v₂` panel orta yüksekliğine göre simetriktir: panel **baş aşağı** (yüz normali etrafında 180°) takılınca dil `v₂`'ye, oluk `v₁`'e geçer.

### 3.2 Panel yön kuralı
- **Doğu (+x) ve güney (−y) yüzleri:** panel normal (dil altta, `v₁`).
- **Batı (−x) ve kuzey (+y) yüzleri:** panel baş aşağı (dil üstte, `v₂`).
- Sonuç: A'nın doğu dili (`v₁`) B'nin batı oluğuna (`v₁`), B'nin batı dili (`v₂`) A'nın doğu oluğuna (`v₂`) girer. Aynı kural ön–arka komşulukta da geçerlidir.
- Duvardaki tüm kutular aynı yöne (öne) bakar; 90° / 180° döndürülmüş kutu duvara girmez. (Tek başına istifte döndürme serbesttir.)

### 3.3 Köşe ve kıskaç
- Köşe ve dikey kıskacın dış yüzlerinde, her iki yükseklikte (`v₁`, `v₂`) yatay oluk: komşunun dili kutu boyunca kesintisiz kayar. İki yükseklik de olduğu için köşe ve kıskaç yön bağımsız kalır.
- Köşe düğümü, yatay kıskaç: raylar kat bandının içinde değil; değişiklik yok.

### 3.4 Eski dikey yan kilit
- Panel, yatay kıskaç, taban ve tavandaki dikey oluk çentikleri kaldırılır. `YAN_KILIT` bayrağı yatay rayları açıp kapatır.

## 4. Hata önleyici anahtar (yeniden)

- Anahtar yine panelin **alt** dilinde, `u = +40`.
- Baş aşağı takılan (batı, kuzey) panellerde anahtar **üstte, `u = −40`**.
- Cepler:
  - **Taban:** dört kenarda `u = +40` (tek kalıp; değişmez).
  - **Tavan:** batı ve kuzey kenarlarında `u = −40` (tavan boya özel olduğu için mümkün).
  - **Yatay kıskaç:** üst oluğunda `u = +40`, alt oluğunda `u = −40`.
- Yakalanan hatalar: doğu/güney panelin baş aşağı takılması (tavan kapanmaz), herhangi bir panelin içi dışına takılması (dudağa çarpar).
- **Yakalanmayan hata:** batı/kuzey panelin normal takılması (taban cebi dört kenarda olduğu için). Duvara takarken komşunun rayı girmez; montajda fark edilir. Açık risk olarak kalır.

## 5. Dikey arayüz: öne kayabilen istif

### 5.1 Kılavuz raylar (L tutucuların yerine)
- Tavanın kilit yüzünde her node için, ön–arka boyunca uzanan iki **kılavuz ray**: `x = K + FIT … K + FIT + WALL` ve simetriği; yükseklik `KILAVUZ_H = 3` mm; ön ve arka uçları pahlı (kayarak giriş).
- Üstteki taban karosunun dişi cebine `FIT` ile oturur: x'te hizalar, y'de serbest.
- Kılavuzların üst taban çerçevesinin altından geçebilmesi için taban karosunun dört kenarında, köşe yakınında (`x = K … K + WALL + 2·FIT` ve simetriği) `KILAVUZ_H + FIT` yüksekliğinde çentik. Panel oluğunun altında kalır (oluk tabanı z = 3.8).
- Kulp süpürme zarfı yalnızca kolların ve tutma yerinin x aralığına daraltılır; kılavuzlar kesilmez.

### 5.2 T kanal (mandalın yerine)
- Tavanın ön ve arka kenar çerçevesinde, her node'da sabit bir **T kanca** (node kenar ortasından `x = −35` mm, kenar çerçevesinin içinde `y = 2 … 18`): boyun `6 × 16` mm (y boyunca), baş `12 × 16` mm.
- Taban karosunun dört kenar çerçevesinde, aynı konumda (her kenarda kenar ortasından −35 mm; tek kalıp, döndürmeye simetrik), çerçeveyi boydan boya geçen **T kanal** (önü ve arkası açık): boyun `z = GAP … 1.6`, baş `z = 1.6 … 3.0`. Panel oluğunun altında 0.8 mm malzeme kalır.
- Taban cebindeki kaburgalar, kanca şeritlerinde `z ≤ 3.2`'ye kadar kırpılır (kanca cebin içinden geçerek arka kanala ulaşır).
- Kutu önden sürülünce kancalar kanallara girer: dikeyde kilitli, öne–arkaya kayabilir.
- **Konum tutucu:** kanca başının üstünde 0.4 mm tümsek, kanalın tavanında son konumda çukur; titreşimde kaymaz, elle çekilince bırakır.
- Eski kayar mandal (sürgü, dil, anahtar deliği) kaldırılır.

### 5.3 Tek sütun istif
- Komşusu olmayan bir sütunda T kancalar istifi dikeyde bir arada tutar; en üstteki kulptan tutulunca tüm sütun kalkar.
- Bu durumda ortadaki kutu öne çekilirse üstündekiler yine düşer (onları taşıyacak komşu yok). Kayar duvar kullanımı en az iki sütun ister.

## 6. Kabul kriterleri (testler)

1. **Duvar kurulumu:** 2 sütun × 2 kat (1×1 kutular) ve 3 sütun × 2 kat: hiçbir parça çakışmaz; yan komşular arası dil–oluk boşluğu `FIT`.
2. **Kayarak çıkarma:** duvarda herhangi bir kutu −y yönünde 0 … `P_XY` boyunca kaydırılırken (örnek adımlar) hiçbir parçaya çarpmaz.
3. **Üstteki düşmez:** alt kutu çıkarıldıktan sonra, üstündeki kutu 1 mm aşağı indirilince yan komşusunun rayına çarpar (rayda asılı).
4. **Kayarak takma:** bir kutu önden, alttaki kutunun üstüne kaydırılarak takılırken çakışmaz.
5. **Dikey kilit:** T kancalı istifte üstteki kutu 1 mm yukarı kaldırılınca kancaya takılır.
6. **Ray sürekliliği:** dil ray, komşu kutunun köşe ve kıskaçlarındaki oluklardan geçer (çok node'lu kutu yanında kaydırma testi).
7. **Anahtar:** doğu panel baş aşağı → tavana çarpar; herhangi bir panel içi dışına → tabana/tavana çarpar.
8. **Kulp ve çekmece:** mevcut kulp ve çekmece testleri geçmeye devam eder.

## 7. Önizleme

- `kutu.export --duvar`: 3 sütun × 2 kat duvar, alt orta kutu yarıya kadar çekilmiş; `?m=duvar`.

## 8. Kapsam dışı

- Kutunun öne kayarken tamamen çıkmasını engelleyen durdurucu (duvar kullanımında istenebilir).
- Duvarın zemine / duvara sabitlenmesi.
- Ray yük hesabı (yan raydan asılı kutu + içerik); prototiple doğrulanacak.

## 9. Açık riskler

1. **T kanal ince:** baş 1.4 mm, panel oluğu altında 0.8 mm malzeme. Dikey çekme kapasitesi prototipte ölçülmeli; yetmezse kanal derinliği için taban çerçevesi kalınlaştırılır.
2. **Batı/kuzey panelin normal takılması** anahtarla yakalanmıyor (bkz. 4).
3. **Kenar sütun:** duvarın en kenarındaki kutu tek yanından asılı kalır; ray burulması prototipte görülmeli.
4. **Tek sütun:** kayar duvar en az iki sütun gerektirir (bkz. 5.3).

## 10. Uygulama notları (2026-10-02)

- Uygulandı: yatay yan raylar (`lib/yan_ray.py`), batı/kuzey baş aşağı kuralı, köşe/kıskaç dış olukları, kılavuz raylar, T kanal (`parts/t_kanal.py`), duvar önizlemesi (`kutu.export --duvar`, `?m=duvar`). Kayar mandal kaldırıldı.
- **Spec'ten sapmalar:**
  - Panel oluğu arkasındaki destek şeridi gerekmedi: komşu dili yüzden yalnızca `RAY_T − 2·GAP + FIT = 2.2` mm girer, deride 1.8 mm kalır.
  - Panel oluğu, köşe kanalına giren yan diller dahil panelin tam boyunca (±86 mm); aksi hâlde komşu dili kanal içindeki deriye sürtüyor.
  - Taban karosunda her kenarda T kanalın yanında **karşı kenarın kancası için düz geçit** (`−T_KANCA_X`) gerekti: kutu önden sürülürken ön kanca üst tabanın arka çerçevesinden geçer.
  - T kanal ölçüleri: boyun `GAP … 1.4`, kanca başı `1.6 … 3.0`, kanal tavanı 3.2 (panel oluğunun 0.6 mm altında). Tutma çıkıntısı 0.9 mm.
  - Kılavuz raylar kilit yüzünün 1 mm altından başlar (çerçeve ve kaburgaların üstüne oturur); cep üstünde kaburga kesişimlerinde taşınır.
  - Kanca başındaki konum tutucu tümsek modellenmedi (açık madde).
- Testler: `test_yan_ray`, `test_yan_kilit`, `test_t_kanal`, `test_duvar` (+ mevcut kulp, çekmece, istif testleri) — toplam 216 test geçiyor.
