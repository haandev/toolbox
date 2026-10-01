# Spec: Tavan modülleri, modüller arası bağlantı ve baskı için bölme

Tarih: 2026-10-02
Önceki: `2026-10-02-acilir-kapak.md` §10 (tavan modülleri), `2026-10-02-moduler-kapak.md` (hücreli yaklaşım — uygulanmadı, `moduler-kapak` dalında kaldı)

## 1. Neden hücreler değil modüller

Hücreli tavanda her node sınırında çerçeve kenarı vardı; birden çok node'a uzanan gömme kulp bu kenarlardan geçemiyordu. Modülde çerçeve yalnız modül çevresinde bir halkadır; modülün içinden kulp serbestçe geçer. Büyük kutular modüllerle döşenir, modüller kamlarla birleşir; baskı için her modül node boyunda parçalara bölünür (modül içinde yine kenar yok).

## 2. Modül tipleri

- **1×1, 2×1, 1×2, 2×2** — her birinde tek kulp, modülün ağırlık merkezinde (1× kulp 1 genişlikte, 2× kulp 2 genişlikte; kulp x boyunca).
- Döşeme: satır satır, önce 2×2, sonra 2×1, sonra 1×2, kalan yerlere 1×1 (`tavan_modulleri`).
- Her modülün kendi çerçevesi, kapağı, menteşesi, mandalları ve kulbu var.

## 3. Modüller arası bağlantı

- Bitişik modül çerçeveleri ek yeri boyunca her node kenarında iki papyon kamla bağlanır (kenar ortasından ±70 mm). Kamlar çerçeve üstünden açılan yuvalara oturur, menteşe boğumlarının altında kalır.
- Çevre kenarlarda kam yok. Böylece kutunun ortasındaki ek yerleri de bağlıdır.

## 4. Baskı için bölme

- `baski_parcalari(mx, my)`: modülün çerçevesi ve kapağı node çizgilerinden (x, y = 200·k) bölünür; kesimlerde `FIT` boşluk; her kesimde papyon kamlar (çerçevede rim boyunca, kapakta güvertede alttan). Her parça ≤ 256 mm.
- 2× kulp baskıda: iki kulp ucu + standart çubuk (Ø12); kalıpta tek parça.
- Kabul: parçalar tabla sınırında, birbirine ve kamlara çakışmaz, birleşmiş hacim tek parçayla uyumlu (kesim boşlukları ve kam yuvaları hariç), kamlar parçaları kilitler.

## 5. Kabul (montaj)

1. 1×2 modül: kulp merkezde, kapak açılır (mevcut modül testleri genişletilir).
2. 4×4 kutu: dört 2×2 modül; modüller arası kamlar; çakışma yok.
3. Mevcut istif, duvar, kapak, kulp testleri geçer.
