# Modüler Kutu Sistemi: Motivasyon ve Ön Tasarım Belgesi

> Bu belge, Claude Code oturumunda projenin başlangıç bağlamı olarak kullanılmak üzere hazırlanmıştır. Burada yazanlar kesinleşmiş kararlar değil, ön tasarımdır. "Açık sorular" bölümündeki maddeler tasarım ilerledikçe netleşecektir.

---

## 1. Motivasyon

### 1.1 Problem

Amaç, her biri tek başına alet çantası olarak kullanılabilen, ama üst üste ve yan yana konduğunda birbirine kilitlenerek çekmeceli, modüler bir yapı oluşturan kutular elde etmek.

Piyasadaki çözümler (Milwaukee Packout, DeWalt TSTAK, Stanley FatMax Pro-Stack, Festool Systainer) bu ihtiyacı karşılıyor ama:

- Pahalılar ve Türkiye'de bulunmaları zor; özellikle Stanley Pro-Stack modülleri çoğu zaman stokta yok.
- Kapalı sistemler: ölçüleri, iç düzeni ve kilit tipini kullanıcı değiştiremiyor.
- Markalar arası uyumsuzlar.

Türkiye'de kolay bulunan ucuz alternatifler (örneğin Mano MT-19) ise üst üste konabiliyor ama birbirine kilitlenmiyor; "metal kilit" yalnızca kapak mandalı.

3D baskı topluluğundaki hazır çözümler (örneğin MakerWorld'deki pixelwave "Gridfinity Case System") ya küçük boyutlu (yaklaşık 23 x 19 cm) ya da remix ve türev üretimini yasaklayan lisanslara sahip. **Bu projede bu tür tasarımlardan geometri kopyalanmayacak; her şey sıfırdan tasarlanacak.**

### 1.2 Vizyon

Hazır bir kutu tasarlamak yerine, **kutu yapmaya yarayan bir parça sistemi** tasarlamak. Lego gibi:

- Az sayıda standart parça (duvar paneli, köşe, kıskaç, taban, tavan).
- Kullanıcı bu parçaları vidalayarak 16 cm'nin katı ölçülerde istediği kutuyu kurar.
- Bütün kutular aynı bağlantı arayüzünü kullandığı için **üst üste, yan yana, her yönden** birbirine kilitlenir.
- Kutunun içi kullanıcıya kalır: çekmece, yandan açılan kapak, bölmeli organizer, düz kutu.
- Herkes tarafından kişiselleştirilebilir ve parametrik olarak yeni ölçüler üretilebilir.

---

## 2. Tasarım İlkeleri

1. **Az parça tipi.** Parça kataloğu küçük kalmalı. Yeni bir parça tipi eklemeden önce mevcut parçalarla çözülüp çözülemeyeceği sorulmalı.
2. **Sabit ızgara.** Tüm bağlantı noktaları sabit bir ızgaraya oturur. Kilit noktalarının yeri kutu boyutuna göre değişmez; böylece farklı boyuttaki kutular birbirine kaydırılmış olarak da kilitlenebilir.
3. **Cinsiyetsiz (hermafrodit) bağlantı.** Kutu-kutu bağlantısında erkek-dişi ayrımı olmamalı. Herhangi bir kutunun herhangi bir yüzü, döndürülmüş olsa bile, başka bir kutunun herhangi bir yüzüne bağlanabilmeli. Bu, sistemin en kritik ve en zor tasarım problemi.
4. **Sökülüp takılabilirlik.** Vidalar plastiğe değil, ısıyla gömülen dişli insertlere (heat-set insert) girer. Kutular defalarca sökülüp yeniden kurulabilmeli.
5. **Rijitlik.** Çok parçalı vidalı kutular paralelkenar gibi yamulmaya yatkındır. Köşe parçası ve taban, dolu kutular üst üste istiflendiğinde sallanmayı engelleyecek kadar rijit olmalı.
6. **Destek gerektirmeyen baskı.** Her parça mümkünse desteksiz basılabilmeli. Baskı yönü, katman çizgileri yük yönüne paralel olmayacak şekilde seçilmeli.
7. **Parametriklik.** Tüm ölçüler tek bir parametre dosyasından gelir. Birim, duvar kalınlığı, vida çapı, tolerans değiştirildiğinde bütün parçalar ona göre yeniden üretilir.

---

## 3. Birim Sistemi

| Parametre | Değer | Açıklama |
|---|---|---|
| Yatay birim (U) | 160 mm | Panel genişliği. Kutu taban ölçüleri U'nun katı. |
| Yükseklik birimi (H) | 80 mm | Duvar paneli yüksekliği. Kutu yüksekliği H'nin katı. |
| Köşe katkısı (K) | ~20 mm / taraf (tahmini) | Köşe parçasının her kenara eklediği ölçü. Doğrulanacak. |

### 3.1 Dış ölçü formülü

Bir kenarda `n` panel varsa:

```
dış_ölçü = n × U + 2 × K
```

Köşe katkısı kenar başına toplam yaklaşık 40 mm (her iki uçta ~20 mm) kabul edilirse:

| Panel sayısı (n) | Panel uzunluğu | Tahmini dış ölçü |
|---|---|---|
| 1 | 160 mm | ~200 mm |
| 2 | 320 mm | ~360 mm |
| 3 | 480 mm | ~520 mm |
| 4 | 640 mm | ~680 mm |

Üstten bakınca hedeflenen kutu ölçüleri: 16x16, 16x32, 16x48, 16x64 ... 64x64 (panel ölçüsü, cm). Köşe katkısıyla dış ölçüler yaklaşık 20x20, 20x36, 36x36 gibi olur.

> **Not:** Ön görüşmede 20x34 ve 34x34 gibi ölçüler de geçti. Yukarıdaki formüle göre 2 panelli kenar ~36 cm çıkıyor, 34 değil. Köşe katkısının gerçek değeri ve formül, köşe parçası tasarlandıktan sonra kesinleşecek. Claude Code bu tutarsızlığı kullanıcıyla netleştirmeli.

### 3.2 Izgara ve sabit bağlantı noktaları

- Her panelin kenarlarında, U ve H'ye bağlı sabit aralıklarla vida/insert delikleri bulunur.
- Kutu-kutu kilit noktaları panel ek yerlerine değil, bu sabit ızgaraya bağlıdır.
- Hedef: 16x32'lik bir kutu, 16x48'lik bir kutunun üstüne 16 cm kaydırılmış olarak da kilitlenebilmeli.

---

## 4. Parça Kataloğu (v0 taslağı)

### 4.1 Duvar paneli
- Ölçü: 160 x 80 mm, kalınlık belirlenecek (ön tahmin 3-4 mm, kaburgalı/nervürlü olabilir).
- Kenarlarda insert delikleri: yan kenarlarda kıskaç ve köşe bağlantısı için, alt ve üst kenarlarda taban ve tavan bağlantısı için.
- Dış yüzde opsiyonel kilit ızgarası (yan yana bağlantı için).

### 4.2 Köşe parçası
- 90 derecelik dikey köşe profili, yüksekliği H (80 mm).
- İki paneli 90 derecede birleştirir.
- Rijitliğin ana kaynağı. Taban ve tavana da bağlanmalı.
- Kenar başına yaklaşık 20 mm katkı (doğrulanacak).

### 4.3 Kıskaç (ek ve kilit parçası)
- İki paneli aynı düzlemde, ek yerinden birleştirir: her iki panelin deliklerine vidalanır.
- Dış şekli aynı zamanda başka bir kutuyla geçme/kilit yeridir. Tek parça iki iş görür.
- Cinsiyetsiz olmalı.

### 4.4 Taban paneli
- 160 x 160 mm modüller veya U'nun katı ölçülerde.
- Alt yüzde, alttaki kutunun tavanıyla eşleşen kilit/oturma geometrisi.
- İsteğe bağlı ayak.
- Mümkünse taban ve tavan aynı panel tipinden türetilir; yalnızca eklentileri (ayak, sap yuvası) farklıdır.

### 4.5 Tavan paneli
- Tabanla aynı ızgara.
- **Sap yuvası:** Taşıma sapı tavanın istenen herhangi bir noktasına bağlanabilmeli.
- Üst yüzde, üstteki kutunun tabanıyla eşleşen kilit geometrisi.

### 4.6 Aksesuarlar (sonraki fazlar)
- Çekmece ve çekmece rayı
- Yandan veya üstten açılan kapak için menteşe ve mandal
- Taşıma sapı
- İç bölmeler ve organizer
- Tekerlekli taban modülü

---

## 5. Bağlantı Arayüzü

Bu bölüm sistemin kalbidir ve en çok iterasyon gerektirecek kısımdır.

### 5.1 Üç bağlantı türü
1. **Panel-panel (aynı düzlem):** Kıskaç ile.
2. **Panel-panel (90 derece):** Köşe parçası ile.
3. **Kutu-kutu:** Dikey (üst üste) ve yatay (yan yana). Kıskacın dış şekli, taban ve tavan kilit geometrisi ile.

### 5.2 Cinsiyetsiz kilit için değerlendirilecek yaklaşımlar
- Simetrik kırlangıç kuyruğu çifti (her parçada hem çıkıntı hem yuva).
- Dönel simetrik pim ve yuva düzeni (90 derece döndürüldüğünde yine eşleşen).
- Mandal veya kanca tipi kilit (kayarak ya da döndürerek kilitlenen).
- Mıknatıslı hizalama ile mekanik kilit kombinasyonu.

Her yaklaşım için küçük test parçaları basılıp denenmelidir.

### 5.3 Yük senaryoları
- Üst üste 3-4 dolu kutu (her biri tahmini 5-10 kg).
- Üstteki kutunun sapından tutup alttaki kutularla birlikte kaldırma.
- Taşıma sırasında yanal darbe.

---

## 6. Malzeme ve Baskı

- **Malzeme:** PETG (öncelikli) veya ASA/ABS. PLA kullanılmamalı: kırılgan ve sıcak araç içinde deforme olur.
- **Vida ve insert:** M3 veya M4 heat-set insert (karar verilecek). Tek veya iki vida boyuyla sınırlı kalınmalı.
- **Baskı ayarları (başlangıç):** 4+ duvar (perimeter), %40-50 dolgu, kilit ve kıskaç parçalarında daha yüksek.
- **Toleranslar:** Geçme yerleri için 0,2-0,3 mm boşluk ile başlanır, tolerans test parçalarıyla kalibre edilir.
- **Tabla boyutu:** 160 mm panel çoğu yazıcıya sığar. Kullanıcının yazıcı modeli ve tabla boyutu netleştirilmeli.

---

## 7. Araç Zinciri

- **Ana CAD:** OpenSCAD. Parametrik, kod tabanlı, ücretsiz.
- **Alternatif:** build123d veya CadQuery (fillet, STEP çıktısı gerekirse).
- **Önizleme:** Three.js ile tarayıcıda 3D konsept görünümü (sunum ve hızlı karar için; baskı dosyası kaynağı değil).
- **Çıktı:** OpenSCAD komut satırıyla STL üretimi (`openscad -o parca.stl parca.scad`).

### 7.1 Önerilen repo yapısı

```
moduler-kutu/
├── README.md
├── docs/
│   └── on-tasarim.md          (bu belge)
├── scad/
│   ├── params.scad            (tüm ölçüler tek yerde)
│   ├── lib/
│   │   ├── insert.scad        (insert deliği modülü)
│   │   └── kilit.scad         (kilit geometrisi)
│   ├── panel_duvar.scad
│   ├── kose.scad
│   ├── kiskac.scad
│   ├── panel_taban.scad
│   ├── panel_tavan.scad
│   ├── test/
│   │   └── tolerans_test.scad
│   └── montaj/
│       └── kutu_16x16x8.scad  (montaj önizleme)
├── stl/                       (üretilen dosyalar)
└── preview/
    └── index.html             (Three.js önizleme)
```

---

## 8. Yol Haritası

| Faz | Hedef | Kabul kriteri |
|---|---|---|
| 0 | Parametre dosyası ve tolerans testleri | Insert deliği ve geçme toleransı test parçası basılır, değerler `params.scad`'e işlenir. |
| 1 | Duvar paneli ve kıskaç | İki panel kıskaçla aynı düzlemde birleşir, ek yeri sallanmaz. |
| 2 | Köşe parçası ve ilk küp | 4 panel + 4 köşe + taban ile 16x16x8 kutu kurulur, rijit durur. |
| 3 | İstifleme | İki kutu üst üste kilitlenir, üstteki kutudan tutunca alttaki de kalkar. |
| 4 | Yan yana kilit ve cinsiyetsiz arayüz doğrulaması | Kutular döndürülmüş hâlde de birbirine kilitlenir. |
| 5 | Tavan ve sap | Sap tavanın farklı noktalarına bağlanabilir. |
| 6 | Boyut çeşitleri | 16x32, 32x32 ve 2H yükseklik kutular kurulur, farklı boyutlar kaydırılmış olarak kilitlenir. |
| 7 | Aksesuarlar | Çekmece, menteşeli kapak, iç bölmeler. |
| 8 | Dokümantasyon ve paylaşım | Montaj kılavuzu, parça listesi, lisans kararı. |

---

## 9. Claude Code İçin Çalışma Talimatları

- Her fazda önce küçük test parçası, sonra tam parça tasarla.
- Tüm ölçüleri `params.scad` üzerinden yönet; parça dosyalarına sabit sayı yazma.
- Her parça için STL üret ve mümkünse ekran görüntüsü/önizleme ile kullanıcıya göster.
- Kararsız kalınan tasarım noktalarında birden fazla seçenek üret ve kullanıcıya sor.
- Başkalarının lisanslı tasarımlarından (özellikle remix yasağı olanlardan) geometri kopyalama; yalnızca genel fikirlerden ilham al.
- Her faz sonunda bu belgedeki "Açık sorular" bölümünü güncelle.

---

## 10. Açık Sorular

1. **Köşe katkısı:** Kenar başına kesin ölçü ne? 20x34 ve 34x34 ölçüleri formülle nasıl uyuşacak?
2. **Yazıcı:** Kullanıcının yazıcı modeli ve tabla boyutu nedir?
3. **Insert boyutu:** M3 mü, M4 mü?
4. **Cinsiyetsiz kilit:** Hangi geometri seçilecek? (Bölüm 5.2)
5. **Taban ve tavan:** 160x160 modüllerden mi birleşecek, yoksa her kutu boyutu için tek parça mı? (Tabla boyutu sınırlayıcı.)
6. **Panel-taban bağlantısı:** Duvarın alt kenarı tabana köşe parçasıyla mı, ayrı bir kenar profiliyle mi bağlanacak?
7. **Gridfinity uyumu:** 160 mm, Gridfinity'nin 42 mm ızgarasına tam bölünmüyor. İç düzende Gridfinity desteği isteniyor mu? İstenirse iç ölçü nasıl ayarlanacak?
8. **Yük kapasitesi:** Kutu başına hedeflenen maksimum ağırlık nedir?
9. **Lisans:** Proje paylaşılacaksa hangi lisansla (örneğin CC BY-SA, açık kaynak)?
