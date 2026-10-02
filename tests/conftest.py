def hacim(sekil) -> float:
    """Boş kesişim build123d'de None dönebilir; 0 hacim say."""
    return 0.0 if sekil is None else float(sekil.volume)


# İki tavan modunun (modül, evrensel) bütün parça türleri
TAVAN_TURLERI = ("cerceve", "kapak", "kapak_mandal", "kulp", "papyon_cerceve",
                 "cerceve_kenari", "cerceve_kenari_cepli", "kapak_hucre", "kam_cerceve", "kam_kapak", "tapa",
                 "mentese_cerceve", "mentese_kapak", "mentese_pimi", "mandal_eki",
                 "kulp_ayagi", "kulp_kolu", "kulp_cubugu")
# Panel üst dilini tutan tavan parçaları (oluk)
OLUK_TURLERI = ("cerceve", "cerceve_kenari", "cerceve_kenari_cepli", "tapa", "mentese_cerceve")
