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
