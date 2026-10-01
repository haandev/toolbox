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
ERKEK_H = 5.0      # tavan bileziğinin kilit yüzünden taşma yüksekliği (taban cebine girer)
ERKEK_PAH = 1.5    # bilezik üst dış kenar giriş pahı
TUTUCU_A = K + FIT # tavan köşe tutucusunun dış yüzü (node kenarından)
TUTUCU_L = 25.0    # köşe tutucusu kol boyu

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

# --- Yan kilit (deneme; YAN_KILIT=False ile kalkar) ---
YAN_KILIT = True
YAN_KILIT_X = 15.0   # dil -x'te, oluk +x'te (panel merkezine göre)
YAN_DIL_W = 10.0
YAN_DIL_H = 3.0      # dilin ped yüzünden taşma boyu

# --- Kilit bölgeleri (bu fazda boş bırakılan hacim) ---
KILIT_W = 60.0     # panel üzerinde yatay
KILIT_H = 50.0     # panel üzerinde dikey
KILIT_KARO = 60.0  # karo üzerinde kare


def kutu_dis(n: int, adim: float) -> float:
    """n node'luk kenarın gerçek dış ölçüsü."""
    return n * adim - 2 * GAP
