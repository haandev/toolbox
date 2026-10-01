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

## 6. Uygulama notları (2026-10-02)

- Uygulandı: 1×2 modül ve döşeme sırası; `lib/papyon.py`; modüller arası kamlar (`papyon_cerceve`, alttan takılır — üstte menteşe boğumları var); `baski.py` (`modul_baski_parcalari`, `kulp_baski_parcalari`); `kutu.export --baski` → `out/baski/*.stl` + `?m=baski_onizleme`.
- Kam konumları her node kenarında ±70 mm (`YUVA_U = 30, 170`).
- **Çerçeve parçaları kesimde kamsız:** kesimler node köşelerindeki vida deliklerine denk gelir; çevrede kıskaç vidaları, içeride modüller arası kamlar tutar.
- **Kapak kamları** kesim boyunca, yuvanın ≥%60'ı malzemeye denk gelen aday konumlarda (önce ±70, olmazsa kenara yakın ±88); 2×1/1×2'de 2, 2×2'de 5 kam.
- **2×2 kapağın ön–arka kesimi** kulp kanalının ortasından geçer: iki yarı kanalın dışındaki uç kamlarla ve kulp mafsal pimiyle tutunur — diğer ek yerlerinden zayıf (prototip).
- 2× kulp baskıda: iki kulp ucu (kol + mafsal pimi + Ø10 çubuk yuvalı göbek) + Ø10 çubuk.
- Çevre kenarlardaki modül kam yuvaları panel oluğu bandına açılır; panel üst dili orada yan desteğini yerel olarak kaybeder.
