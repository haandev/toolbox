"""Kalıplanabilirlik raporları."""
from build123d import GeomType, Part, Vector


def egimsiz_yuz_sayisi(parca: Part, cekme: tuple[float, float, float]) -> int:
    """Çekme yönüne tam paralel (eğimsiz) düzlemsel yüzlerin sayısı."""
    yon = Vector(*cekme).normalized()
    sayi = 0
    for yuz in parca.faces():
        if yuz.geom_type != GeomType.PLANE:
            continue
        if abs(yuz.normal_at().dot(yon)) < 1e-6:
            sayi += 1
    return sayi
