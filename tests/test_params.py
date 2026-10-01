import pytest
from build123d import Box
from kutu import params as p
from kutu.kalip import egimsiz_yuz_sayisi


def test_turetilen_degerler():
    assert p.K == 20
    assert p.T == 15   # H = 70: kalın karo (evrensel tavan kapağı 8 mm)
    assert p.PANEL_L == 172
    assert p.PANEL_H == 78   # H 70 + alt/üst dil DIL_V = 4
    assert p.DIL_V < p.DIL


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_yatay_izgara_esitligi(n):
    # köşe + n panel + (n-1) kıskaç + köşe = n adım
    assert p.K + n * p.U + (n - 1) * 2 * p.K + p.K == n * p.P_XY


@pytest.mark.parametrize("m", [1, 2, 3])
def test_dikey_izgara_esitligi(m):
    # taban + m panel + (m-1) sırt sırta karo çifti + tavan = m adım
    assert p.T + m * p.H + (m - 1) * 2 * p.T + p.T == m * p.P_Z


def test_kutu_dis_olcusu():
    assert p.kutu_dis(1, p.P_XY) == 199
    assert p.kutu_dis(2, p.P_XY) == 399
    assert p.kutu_dis(1, p.P_Z) == 99


def test_kalip_kurallari():
    assert p.RIB == pytest.approx(0.6 * p.WALL)
    assert p.R_IN_MIN == pytest.approx(0.5 * p.WALL)


def test_cep_kule_sigar():
    # köşe cebi kuleyi almalı
    cep = (p.K - p.WALL) - p.CEP_IC
    assert cep > p.KULE_OD
    # kıskaç kuleleri cebe sığmalı ve birbirine değmemeli
    assert p.KISKAC_KULE_X + p.KULE_OD / 2 < p.KISKAC_CEP_YARI
    assert p.KISKAC_KULE_X - p.KULE_OD / 2 > 0


def test_egimsiz_yuz_sayisi_kutu():
    # Z yönünde çekilen düz kutunun 4 yan yüzü eğimsizdir
    assert egimsiz_yuz_sayisi(Box(10, 10, 10), (0, 0, 1)) == 4
