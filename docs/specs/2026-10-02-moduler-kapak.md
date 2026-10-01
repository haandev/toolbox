# Spec: Modüler kapak — hücreler ve bağlantı parçaları

Tarih: 2026-10-02
Önceki spec: `2026-10-02-acilir-kapak.md` (§10 "tavan modülleri"nin yerini alır; çerçeve/kapak/menteşe/mandal ilkeleri geçerli)

## 1. Amaç

- Her boyutta kutunun (ör. 4×4 node) tavanı **aynı birkaç parçadan** kurulabilsin.
- Kapağın nasıl gruplanacağına kullanıcı karar versin: tek büyük kapak, satır satır kapaklar ya da node node kapaklar.
- Her parça yaygın 3D yazıcı tablasına sığsın (≤ 256 mm) ve **kolay birleşsin**.
- Kalıp üretimi için boya özel tek parça çerçeve/kapak seçeneği kalsın (`cerceve(nx, ny)`, `kapak(nx, ny)`).

## 2. Parça kataloğu

| Parça | Adet tipi | Açıklama |
|---|---|---|
| **Çerçeve hücresi** | 1 | 1×1 node halka; dört kenarda panel oluğu, 12 vida deliği, dört kenarda bağlantı yuvaları. 90° simetrik. |
| **Kapak hücresi — düz** | 1 | 1×1 node kapak; T raylar; dört kenarda bağlantı yuvaları. |
| **Kapak hücresi — kanallı** | 1 | Ortasından x yönünde kulp kanalı geçen kapak hücresi (kanal kenarlardan açık, yan hücreye devam eder). |
| **Kapak hücresi — yarım kanallı** | 1 | Kulp kanalının yarısı bir kenarda; 180° çevrilmiş ikizi ile ek yerinde tam kanal oluşturur (çift satırlı gruplarda kulp ortada). |
| **Papyon kam** | 1 | İki hücreyi ek yerinde birleştirir; yukarıdan iki hücrenin kırlangıç yuvasına basılır. Çerçeve–çerçeve ve kapak–kapak. |
| **Menteşe kanadı (çerçeve)** | 1 | Yarım papyon + boğumlar; çerçeve hücresinin bir kenar yuvasına takılır. |
| **Menteşe kanadı (kapak)** | 1 | Yarım papyon + boğumlar; kapak hücresinin kenar yuvasına takılır. |
| **Menteşe pimi** | — | Standart çubuk (ör. Ø3 çelik), grubun genişliği kadar kesilir. |
| **Kapak mandalı + yuva kanadı** | 2 | Mandal kapak hücresinin ön kenar yuvasına, karşılığı (anahtar deliği) çerçeve kenar yuvasına takılır. |
| **Kulp ucu** | 1 (×2) | Mafsal + kol; kanallı hücrelerin kanal uçlarındaki yuvaya takılır. |
| **Kulp tutma çubuğu** | — | Standart boru/çubuk (ör. Ø16 alüminyum), kulp boyunda kesilir. |

## 3. Bağlantı yuvası (standart arayüz)

- Her hücre kenarında, kenar ortasından ±`YUVA_X` (= 50 mm) iki **kırlangıç yuvası**: üstten açık, kenara dik, yarım papyon biçimli.
- Bir **papyon kam** iki komşu hücrenin karşılıklı yarım yuvalarına oturur ve onları kenara dik yönde birbirine kilitler. Hücreler arası boşluk `GAP` korunur.
- Aynı yuvalara papyon yerine **menteşe kanadı**, **mandal** ya da **kulp ucu** takılabilir; hepsinin takılan kısmı yarım papyondur.
- Yuvalar çerçeve hücresinde çerçevenin üst yüzünden, kapak hücresinde kapak güvertesinin altından açılır (kapak üst yüzü T raylar için temiz kalır).

## 4. Gruplama (kullanıcının kararı)

- Kullanıcı kapak hücrelerini **gruplara** ayırır; bir grup tek kapak gibi açılır.
- Grup içindeki ek yerleri papyon kamlarla birleşir; grupların arasında kam yok.
- Her grubun **arka kenarındaki** her hücreye menteşe kanatları, **ön kenarındaki** her hücreye mandal takılır. Arka kenarı kutunun içinde kalan grupların menteşesi, arkalarındaki çerçeve hücresinin kenar yuvasına takılır (çerçeve her yerde sürekli).
- **Çerçeve** her zaman tek bütün: bütün çerçeve hücreleri papyonlarla birleşir; kutunun ortasındaki ek yerleri de bağlıdır (iç ek yeri sarkması çözülür).
- Montaj arayüzü: `kutu(..., kapak_gruplari=[(i0, j0, gx, gy), ...])`; verilmezse varsayılan **tek grup** (tüm tavan tek kapak).

## 5. Kulp

- Kulp her grubun **ağırlık merkezinde**: tutma yeri açılınca grubun merkezinin üstünde (dengeli asılma).
- Grubun satır sayısı tekse kulp kanallı hücre satırında (grubun orta satırı), çiftse iki orta satırın ek yerinde (yarım kanallı hücre çifti).
- Kulp boyu grubun genişliği kadar: iki kulp ucu + boyuna kesilmiş çubuk. Kanal, kanallı hücreler boyunca kesintisiz.
- Kalıp üretiminde kulp tek parça da olabilir (`kulp(n)` korunur).

## 6. Kabul kriterleri

1. 1×1, 2×1, 2×2, 3×2, 4×4 kutular yalnızca §2'deki parçalarla kurulur; parça sayıları beklenen.
2. Kurulu tavan çakışmasız; papyonlar her iki hücreye `FIT` ile oturur; çerçeve iç ek yerleri bağlı (hücreler ayrılamaz: kam varken komşu hücre 1 mm kaydırılınca çarpar).
3. 4×4 kutu: tek grup (tek kapak) ve 2×2 grup (dört kapak) seçenekleri; her grup açılırken çakışmaz.
4. Her grubun açık kulbu grup merkezinin üstünde.
5. Her hücre ≤ 256 mm (baskı tablası); papyon, kanat, mandal, kulp ucu küçük parçalar.
6. İstif, kayar duvar, T ray testleri geçer (T raylar hücre ek yerlerinde kesintili olabilir; üst kutu kaymaya devam eder).

## 7. Açık riskler

1. Papyon kamların taşıma kapasitesi (kapak grubunun kulptan kaldırılması) — prototip.
2. Ek yerlerinde T ray kesintisi üstteki kutunun kaymasında takılma yaratabilir — pah ile giriş.
3. Hücreli kapak tek parçaya göre daha esnek; büyük grupların rijitliği prototipte görülmeli.
