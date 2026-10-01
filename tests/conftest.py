def hacim(sekil) -> float:
    """Boş kesişim build123d'de None dönebilir; 0 hacim say."""
    return 0.0 if sekil is None else float(sekil.volume)
