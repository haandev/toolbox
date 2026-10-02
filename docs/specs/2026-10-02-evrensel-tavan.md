# Spec: Evrensel tavan ve kaldırmalı kulp

Tarih: 2026-10-02
Önceki: `2026-10-02-tavan-modul-baski.md` (tavan modülleri — bunun yerini alır; kalıp üretimi için boya özel tek parça seçenek korunur), `2026-10-02-moduler-kapak.md` (hücre fikri — evrensel yuva ile yeniden)

## 1. Şartlar (kullanıcı)

1. **Tek tip tavan parçası:** çerçeve hücresi ve kapak hücresi birer tip; yan yana eklenerek her ölçü kurulur (custom ölçü).
2. **Tek kulp tasarımı** 1×1, 2×1 ve 2×2 gruplarını **tam ortadan** taşır.
3. Kapak grupları kullanıcı seçimidir (tek kapak / satırlar / bloklar).
4. Her parça 256 mm baskı tablasına sığar ve kolay birleşir; kalıpta da aynı parçalar kullanılabilir.

## 2. Evrensel yuva

- Her hücre kenarında, kenar boyunca `YUVA_U = 40` ve `160` mm'de **yarım papyon yuvası**; iki komşu hücrenin yarım yuvaları ek yerinde **tam yuva** oluşturur.
- Kapak hücresinin **orta çizgisinde** (y = 100) x = 40 ve 160'ta iki **tam yuva**.
- Yuvalar çerçevede tam boy (üstten alta), kapakta tam boy açıktır.
- Her yuvaya bir **ek parça** takılır:

| Ek | Nerede | İşlev |
|---|---|---|
| Birleştirici kam | iç ek yerleri | iki hücreyi kilitler (çerçeve–çerçeve, kapak–kapak) |
| Tapa | çevre kenarlar (çerçevede oluk profilli), boş yuvalar | panel oluğunu tamamlar / kapatır |
| Menteşe eki (çerçeve / kapak) | grubun arka kenarı (40: çerçeve, 160: kapak) | boğum + pim |
| Mandal eki | grubun ön kenarı | kapağı kilitler |
| Kulp ayağı | kulp konumları (§4) | dikey kılavuz kovan + ayak |

## 3. Hücreler

- **Çerçeve hücresi (1×1):** halka; panel oluğu dört kenarda; 12 vida deliği; kenar yuvaları (tam boy). Yan yana kamlarla birleşir → kutunun tüm çerçevesi tek bütün.
- **Kapak hücresi (1×1):** her kenardan menteşe payı kadar içeride; T raylar; kenar yuvaları ve orta çizgi yuvaları; **orta kanal** (y = 100 boyunca x yönünde) ve **ön/arka kenar yarım kanalları** (iki satırın yarım kanalları ek yerinde tam kanal olur).

## 4. Kaldırmalı kulp

- Parçalar: iki **kulp ayağı** (yuvaya oturan papyon dış gövdeli kılavuz kovan + içinde kayan ayak) ve **tutma çubuğu** (standart alüminyum yassı çubuk, 25×5 mm, boyuna kesilir).
- Dinlenmede çubuk kanalda, kilit yüzünün altında yatar; kullanırken ayaklar kovanlarda `KULP_KALDIRMA` (≈35 mm) yukarı kayar ve durdurucuya dayanır. Tutma yeri her zaman grup merkezinin tam üstünde.
- Konumlar (grup orijinine göre):

| Grup | Ayaklar | Kanal |
|---|---|---|
| 1×1 | (40, 100), (160, 100) — orta çizgi yuvaları | orta kanal |
| 2×1 | (40, 100), (360, 100) | iki hücrenin orta kanalları |
| 2×2 | (40, 200), (360, 200) — ek yerindeki tam yuvalar | iki satırın yarım kanalları |

- Kovanlar kapağın altına sarkar; 2×2'de çerçeve ek yerindeki tam boy yuvalardan geçer. Kulp kapağa bağlıdır; yük kapak → menteşe/mandal → çerçeve yolunu izler.

## 5. Ölçü bedeli

- Kanal 26 × 6 mm; kapak `KAPAK_H = 8`. Çerçevenin panel oluğunun üstünde `WALL` kadar et kalması için **H = 70, T = 15** (ızgara adımı aynı; iç yükseklik 76 → 70).

## 6. Kabul kriterleri

1. Çerçeve ve kapak hücresi tek tip; 1×1, 2×1, 1×2, 2×2, 3×2, 4×4 kutular yalnız bu hücreler ve eklerle kurulur; çakışma yok; her parça ≤ 256 mm.
2. Kamlar hücreleri kilitler (kam varken komşu 1 mm kaydırılınca çarpar).
3. Kulp 1×1, 2×1, 2×2 gruplarında: dinlenmede kilit yüzünün altında, kaldırılmışken tutma yeri grup merkezinin üstünde; istifte üst kutuya değmez.
4. Kapak grupları açılır (arka grup tam, ön grup ~40°; arka açıkken tam).
5. İstif, kayar duvar, çekmece testleri geçer.

## 7. Uygulama aşamaları

1. Ölçü değişimi (H = 70) ve mevcut testler.
2. Hücreler, evrensel yuvalar, birleştirici kam, tapa, menteşe ve mandal ekleri, gruplar.
3. Kaldırmalı kulp (ayak, kovan, çubuk) ve 1×1 / 2×1 / 2×2 konumları.
4. Varsayılan tavanı evrensele geçir; modül tavan kalıp seçeneği olarak kalır. Önizleme ve baskı dışa aktarımı.

## 8. Açık riskler

- Tam boy kenar yuvaları çerçeveyi zayıflatır; çevre kenarlarda tapalar panel oluğunu tamamlamalı.
- Ön grup açılma sınırı (~40°) T raylar nedeniyle sürer.
- Kaldırmalı kulbun ayak–kovan boşluğu ve durdurucusu prototipte ayarlanmalı.

## 9. Değişiklik: kaldırmalı kulp yerine paralel kollu katlanır kulp (2026-10-02)

Kaldırmalı kulbun kılavuz kovanları ve ayakları 25 mm kaldırma için kapağın altına ~65 mm sarkıyor (kutu içini ve çekmeceyi işgal ediyor). Yerine:
- **Kulp ayağı:** yuvaya takılan ek; yuvanın içinde kanalın iki yanında yanaklar, kısa pimler (eksen y, kanal ortası yüksekliğinde).
- **Kollar:** her ayakta kanalın iki yanında birer yan plaka (`KOL = 25`), ayakta ve uçta pimli.
- **Tutma çubuğu:** 16×5 mm alüminyum yassı çubuk, kol uçlarına pimli; iki ayak arası boyda.
- Katlıyken kollar +x yönünde yatık, çubuk kanalda 25 mm kaymış; hiçbir parça kapağın altına sarkmaz.
- Kaldırınca kollar dikleşir, çubuk paralelkenarla yatay kalarak 25 mm yükselir; iki ayağın tam ortasında = grubun ağırlık merkezinin üstünde.
- Kanal `KANAL_W = 22`.

## 10. Uygulama notları (2026-10-02)

- Uygulandı: `parts/evrensel.py` (çerçeve hücresi, kapak hücresi, kam — çerçevede 6.3, kapakta kanal altında 2.3 mm yükseklik —, tapa, menteşe çerçeve/kapak ekleri, mandal eki, kulp ayağı/kolu/çubuğu), `kutu(..., tavan="evrensel")` **varsayılan**, `kapak_gruplari`, `mandal_acik`, `montaj.evrensel_grup_ac()`. Modül tavan `tavan="modul"` ile kalıp seçeneği olarak duruyor.
- Ölçü: H = 70, T = 15, kapak 8 mm.
- **Sapmalar:**
  - Kaldırmalı kulp yerine paralel kollu katlanır kulp (§9); kanal 22 mm, çubuk 16×5.
  - Çerçeve yuvalarına kenar ortası (100) eklendi: grup sınırlarında menteşe (x = 160) ve mandal (x = 160) yuvaları dolu olduğundan çerçeve sürekliliği 40 ve 100'deki kamlarla sağlanır.
  - Menteşe ekleri arka kenarda 180° çevrik: çerçeve eki x = 160, kapak eki x = 40.
  - Çerçeve hücresinin bir **yönü** var: baş aşağı panellerin anahtar cepleri yalnız kuzey ve batı kenarlarda (simetrik olsaydı güney/doğu paneli baş aşağı takılınca yakalanmazdı).
  - Mandal eki çerçevenin altına takılan dudakla kilitler; açmak için öne `MANDAL_GERI` esnetilir.
  - Kulp yalnız 1×1, 2×1, 2×2 gruplarına takılır; diğer grup boylarında kulp yok (kullanıcı grubu buna göre seçer).
- Testler: `test_evrensel.py`, `test_evrensel_kulp.py` (+ tüm mevcut testler evrensel varsayılanla), toplam 308.

## 11. Değişiklik: çerçeve kenar şeritleri ve sökülebilir köprüler (2026-10-02)

Çerçeve hücresi her node'un çevresinde halka olduğundan büyük kutularda iç ek yerlerinde 40 mm'lik kirişler kalıyor, büyük eşya üstten girmiyordu. Yerine:
- **Çerçeve kenar şeridi** (`cerceve_kenari`): hücre halkasının bir kenarı; K genişliğinde, uçları hücre köşesinden 45° pahlı (dört şerit = eski halka). Panel oluğu, yuvalar, köşe vida delikleri. Anahtar cepli çeşidi (`cep=True`) kuzey ve batı kenarlarda.
- **Çevre** kenarlarda şerit her zaman; **iç ek yerlerinde** sırt sırta iki şerit = **köprü**, kamlarla birleşir. `kutu(..., kopru=False)`: grup içi köprüler yok → kapak grubunun altı tek büyük açıklık. Kapak grupları arasındaki köprüler menteşe ve mandal için her zaman takılı.
- Bedel: köprüsüz büyük kapak, üstteki kutunun yükünü alttan desteksiz taşır (kapak hücreleri yalnız kamlarla bağlı); ağır istifte köprüler takılı kalmalı. Köprüsüz çevre ek yerlerinde şerit uçları arasında kıskaç üstünde küçük üçgen boşluk kalır.
- Vitrinde "İç köprüler" seçeneği.
