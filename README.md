# Modüler kutu sistemi

200 × 200 × 100 mm node ızgarasında, yan yana ve üst üste kilitlenen; enjeksiyon kalıbına uygun, 3D yazıcıda (256 mm tabla) prototiplenebilen modüler alet kutusu sistemi. Parametrik CAD: [build123d](https://github.com/gumyr/build123d).

**Canlı vitrin:** https://haandev.github.io/toolbox/ — kutu ölçüsünü (node), kulbu, çekmece/kapalı duvarı seç; parça listesi anında güncellenir. "İstife ekle" ile kutularını istif alanında yan yana/üst üste diz.

## Özellikler

- Kutular node'ların x, y, z birleşimi; erkek/dişi istif ve T ray kilidi.
- Yan raylar: duvardaki her kutu çekmece gibi dışarı çekilir, üstündekiler komşu raylarda asılı kalır.
- Evrensel tavan: tek tip çerçeve ve kapak hücreleri yan yana eklenerek her ölçüye; kapak grupları kullanıcı seçimi; menteşe ve mandal ekleri.
- Paralel kollu katlanır kulp: her kapak grubunun tam ortasında; katlıyken kapak yüzünün altında.
- Kutu içi çekmeceler, yan tutma girintileri.

## Kullanım

```bash
uv sync
uv run pytest                      # geometri ve çakışma testleri
uv run python -m kutu.vitrin       # yerel vitrin: http://localhost:8767/preview/vitrin.html
uv run python -m kutu.export --baski   # baskı STL'leri → out/baski
uv run python -m kutu.site         # GitHub Pages için statik vitrin → site/
```

Tüm ölçüler `src/kutu/params.py` içinde; tasarım kararları `docs/specs/`.
