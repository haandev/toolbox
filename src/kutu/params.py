"""Modüler kutu sistemi — tüm ölçüler (mm). Parça dosyalarında sabit sayı yazılmaz."""

# --- Izgara (girdi) ---
P_XY = 200.0   # yatay node adımı
P_Z = 100.0    # dikey node adımı
U = 160.0      # panel adımı (görünür açıklık)
H = 80.0       # panel yüksekliği (görünür açıklık)
GAP = 0.5      # komşu kutular arası taraf başı boşluk

# --- Türetilen ---
K = (P_XY - U) / 2   # köşe katkısı (20); kıskaç genişliği 2K
T = (P_Z - H) / 2    # karo katkısı (10)

# --- Kalıp kuralları ---
WALL = 2.5
RIB = 0.6 * WALL
RIB_D = 6.0          # kaburga derinliği (deriden içeri)
DRAFT_OUT = 1.5      # derece
DRAFT_IN = 1.0       # derece
R_IN_MIN = 0.5 * WALL
FIT = 0.2            # geçme boşluğu, prototiple kalibre edilir

# --- Kanal / dil ---
LIP = 1.5                  # kanal dış dudağı; panel dış yüzü bu kadar gömük
DIL = 6.0                  # panel dilinin kanal/oluk içine giriş boyu
PANEL_L = U + 2 * DIL      # 172
PANEL_H = H + 2 * DIL      # 92
PANEL_KABURGA_X = (-55.0, -35.0, 35.0, 55.0)   # dikey kaburga konumları (panel merkezine göre)

# --- Vida / kule ---
PROTO = True               # True: heat-set insert deliği (prototip)
VIDA_D = 4.0
KULE_OD = 8.5
KULE_DELIK = 0.8 * VIDA_D  # seri üretim, plastik vida (3.2)
INSERT_DELIK = 4.0         # M3 heat-set insert
GECIS_DELIK = 4.5          # karo vida geçiş deliği

# --- Köşe / kıskaç cepleri ---
CEP_IC = GAP + LIP + WALL + FIT + WALL      # dış yüzden cebe mesafe (7.2)
CEP_BOY = (H - WALL) / 2                     # alt ve üst cep derinliği; ortada WALL kalınlığında ara duvar
KOSE_R = 5.0                                 # köşe dış yuvarlatma
KOSE_KULE = (CEP_IC + (K - WALL)) / 2        # köşe kulesinin x=y konumu
KISKAC_CEP_YARI = K - DIL - FIT - WALL       # kıskaç cebinin yarı genişliği (11.3)
KISKAC_KULE_X = KISKAC_CEP_YARI - KULE_OD / 2 - 0.5   # kıskaç kuleleri ±x

# --- Karo ---
KARO_RIB_ARALIK = 40.0
KILAVUZ_H = 3.0    # tavan kılavuz raylarının kilit yüzünden yüksekliği (taban cebine girer; panel oluğunun altında)
KILAVUZ_A = K + FIT  # kılavuz rayın dış yüzü (node kenarından)
KILAVUZ_PAH = 1.5  # kılavuz ray ön/arka uç pahı (kayarak giriş)

# --- Gömme kulp (tek parça tavanın içinde, kilit yüzünün altında) ---
KULP_W = 24.0          # tutma yeri genişliği
KULP_H = 12.0          # kulp kesit yüksekliği
KULP_KOL = 40.0        # mafsal ekseni ile katlı tutma yeri arası
KOL_T = 8.0            # kulp kolu kalınlığı (eksen boyunca)
MAFSAL_L = 8.0         # mafsal bloğu eksen boyu
MAFSAL_W = 10.0
PIM_D = 4.6

# --- Hata önleyici anahtar (panel yalnız doğru yönde takılır) ---
ANAHTAR_X = 40.0     # panel alt dilinde, merkezden +x
ANAHTAR_W = 10.0
ANAHTAR_T = 2.0      # dilin iç yüzünden içe çıkıntı

# --- T kanal (dikey kilit; kutu öne kayarak takılır/çıkar) ---
T_KANCA_X = -35.0    # kanca merkezi, node kenar ortasından (güney kenar)
T_KANCA_Y0, T_KANCA_Y1 = 2.0, 18.0   # kanca, tavan kenar çerçevesinin içinde
T_BOYUN_W = 6.0
T_BAS_W = 12.0
T_BOYUN_Z1 = 1.4     # taban yerel z: kanalın boyun bölgesi GAP … 1.4 (tutma çıkıntısı)
T_BAS_Z0 = 1.6       # kanca başı (kutu üstünden, = üst taban yerel z)
T_BAS_Z1 = 3.0
T_KANAL_Z1 = 3.2     # kanal tavanı; panel oluğunun (3.8) altında

# --- Çekmece ---
CEKMECE_B = 0.5      # çekmece ile köşe/kıskaç yüzleri arası yan boşluk
TEKNE_ALT = GAP + 1 + KULP_H + 1 + WALL   # tavan kulp teknesinin kutu üstünden sarkması
CEKMECE_TUTAMAK_W = 60.0
CEKMECE_TUTAMAK_H = 15.0
RAF_KENAR = GAP + LIP + WALL + RIB_D + FIT   # raf kenarı: üst kat panel kaburgalarının içinde
RAF_RIB_D = 18.0     # raf altı kaburga derinliği (kat arası bantta, alt çekmecenin üstünde)
CEKMECE_YOL = 120.0  # durdurucuya kadar çekme boyu
DURDURUCU_Y0 = 12.0  # taban/raf üstündeki durdurucu çıkıntısı (kenardan içe)
DURDURUCU_L = 4.0
DURDURUCU_W = 8.0
DURDURUCU_H = 2.0
TUTUCU_TUMSEK = 0.6  # kapalı tutucu: oluk tavanındaki tümsek

# --- Malzeme (PP kopolimer) ---
MALZEME_E = 1.3e9    # Pa

# --- Yan ray (kayar duvar; YAN_KILIT=False ile kalkar) ---
YAN_KILIT = True
RAY_D = 20.0         # raylar panel orta yüksekliğinden ±RAY_D
RAY_H = 8.0          # dil ray yüksekliği
RAY_T = 3.0          # dil rayın şerit yüzünden taşması
RAY_V1 = T + H / 2 - RAY_D   # dil (normal panel), kat tabanından
RAY_V2 = T + H / 2 + RAY_D   # oluk (normal panel)

# --- Kilit bölgeleri (bu fazda boş bırakılan hacim) ---
KILIT_W = 60.0     # panel üzerinde yatay
KILIT_H = 50.0     # panel üzerinde dikey
KILIT_KARO = 60.0  # karo üzerinde kare


def kutu_dis(n: int, adim: float) -> float:
    """n node'luk kenarın gerçek dış ölçüsü."""
    return n * adim - 2 * GAP
