# Spec: Açılır kapak (menteşe + kilitli mandal)

Tarih: 2026-10-02
Önceki spec'ler: `2026-10-01-faz0-2-temel-parcalar.md`, `2026-10-01-kayar-duvar.md` (tavan bölümlerini değiştirir)

## 1. Amaç

Kutunun içine üstten erişim: tavan açılabilir bir kapak olsun. Kapak kapalı ve kilitliyken, kutu kulptan tutulduğunda kapak açılmasın ve kutu bütün kalsın.

## 2. Bölünme

Tavan (`tavan(nx, ny)`) yatayda ikiye ayrılır. Yerel çerçeve aynı: z = 0 kutunun nominal üstü, tavan z = −T … −GAP.

### 2.1 Üst çerçeve — `cerceve(nx, ny)`
- Kutu boyunda halka: dış `[GAP, W−GAP] × [GAP, D−GAP]`, iç açıklık `[K, W−K] × [K, D−K]`, z `−T … −KAPAK_H − GAP`.
- Panel oluğu (altta, `DIL_V + FIT`), köşe/kıskaç vida delikleri, baş aşağı paneller için anahtar cepleri: tavandan aynen taşınır.
- Köşelere ve kıskaçlara vidalıdır; kutuyu bütün tutan parça budur.

### 2.2 Kapak — `kapak(nx, ny)`
- Tam üst yüzey: `[GAP, W−GAP] × [GAP, D−GAP]`, z `−KAPAK_H − GAP … −GAP` (`KAPAK_H = 5.3`): altta `WALL` güverte, üstte kaburgalar.
- T raylar, kulp oyuğu/teknesi ve mafsal blokları kapakta (tavandan taşınır). Tekne çerçeve açıklığından aşağı sarkar; çerçeve iç yüzüne `FIT` boşluk.
- Vidalar kapağın altında kalır.

## 3. Menteşe

- Eksen x boyunca, kapağın arka üst kenarında: `y = D − GAP − MENTESE_R`, `z = −GAP − MENTESE_R` (`MENTESE_R = 3`).
- Eksen boyunca sırayla çerçeve ve kapak boğumları (`MENTESE_BOGUM` boyunda, aralarında `FIT`), çerçeve boğumlarından geçen pim (r = 1.5); kapak boğumlarında `pim + FIT` delik.
- Kapak, eksenin arkasında yalnızca boğumlar kadar malzeme taşır; çerçevenin arka üstü eksenin altında kalır. Böylece kapak 0–100° açılırken çerçeveye sürtmez.
- Açılma: kapak arka kenarı kutu arkasından en çok `MENTESE_R` kadar taşar (ızgara içinde).

## 4. Kapak mandalı

- Her node'un ön kenarında, node ortasında (T raylar ±35 mm'de) bir **kayar sürgü** kapağın içindeki cepte; `KAPAK_MANDAL_YOL = 10` mm.
- Sürgüden aşağı inen kanca, çerçevenin ön kenarındaki anahtar deliği biçimli yuvaya girer: giriş penceresi + altında oda; kilitliyken kanca başı yuvanın tutma çıkıntısının `FIT` altında.
- Sürgüye bağlı dil kapağın ön yüzüne uzanır; dışarıdan parmakla itilir.
- Yük yolu (kulptan kaldırma): kulp → kapak → arkada menteşe pimi, önde mandal kancaları → çerçeve → köşeler → paneller → taban.

## 5. Duvar ve istifle ilişki

- Üstünde kutu olan kutunun kapağı açılmaz (T raylar kapağı üst kutuya bağlar); önce kutu öne çekilir, sonra kapak açılır. Çekmeceli kutuların çekmeceleri doğrudan açılır.
- Kapağın açılırken arkaya taşması `MENTESE_R`'yi geçmez; arkasında kutu olsa bile açılır (kutu önce öne çekildiği için).

## 6. Kabul kriterleri (testler)

1. Kapalı ve kilitli: çerçeve, kapak, mandallar, kulp ve gövde çakışmaz (1×1, 2×1, 2×2).
2. Kilitliyken kapak 1 mm kaldırılınca mandal kancası ve menteşe pimi takılır.
3. Mandal açıkken kapak 0 … 100° açılırken (adımlarla) çerçeveye, gövdeye, panellere çarpmaz; kulp katlı.
4. Kapak açıkken arkaya taşma ≤ `MENTESE_R`.
5. Mevcut istif, kayar duvar, kulp, çekmece testleri geçer (tavan → çerçeve + kapak).

## 7. Önizleme

- `kutu.export --kapak`: kapağı açık 1×1 ve 2×1 kutular; `?m=kapak`.

## 8. Açık riskler

1. **Mandal ve menteşe kapasitesi:** T ray ~1950 N/node taşırken kapak bağlantısı (mandal kancası, menteşe pimi) daha zayıf olabilir; kulptan kaldırma yükü buradan geçer. Prototipte ölçülmeli.
2. Kapak 5.3 mm: eski tavandan ince; rijitlik T raylar ve tekne ile sağlanıyor.
3. Mandalın kendiliğinden açılmasını engelleyen detent modellenmiyor.
4. Kapak contası (toz/su) kapsam dışı.
