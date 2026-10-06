import hid
import time
import ctypes

# ============================================================
# FS-01
# ============================================================

VID = 0x8088
PID = 0x0015
USAGE_PAGE = 0xFF00

PACOTE_PEDAL = [0x66, 0xCC, 0x03, 0x00, 0x01]

INTERVALO_MINIMO = 0.30


# ============================================================
# WINDOWS - TECLA ESPAÇO
# ============================================================

VK_SPACE = 0x20

KEYEVENTF_KEYUP = 0x0002


def pressionar_espaco():

    # Pressiona
    ctypes.windll.user32.keybd_event(
        VK_SPACE,
        0,
        0,
        0
    )

    time.sleep(0.05)

    # Solta
    ctypes.windll.user32.keybd_event(
        VK_SPACE,
        0,
        KEYEVENTF_KEYUP,
        0
    )


# ============================================================
# LOCALIZAR PEDAL
# ============================================================

def localizar_pedal():

    dispositivos = hid.enumerate(VID, PID)

    for dispositivo in dispositivos:

        if dispositivo.get("usage_page") == USAGE_PAGE:
            return dispositivo

    return None


# ============================================================
# PRINCIPAL
# ============================================================

print("=" * 55)
print("       FS-01 - DISPARADOR DA CAMERA")
print("=" * 55)

pedal = localizar_pedal()

if pedal is None:

    print("\n[ERRO] FS-01 não encontrado.")

    input("\nENTER para sair...")
    exit()


print("\nFS-01 encontrado!")
print("Produto:", pedal.get("product_string"))

device = hid.device()

try:

    device.open_path(pedal["path"])
    device.set_nonblocking(True)

    print("\nPedal conectado.")
    print("Aguardando acionamento...\n")

    ultimo_disparo = 0

    while True:

        dados = device.read(64)

        if dados:

            if dados[:5] == PACOTE_PEDAL:

                agora = time.time()

                if agora - ultimo_disparo >= INTERVALO_MINIMO:

                    print("PEDAL -> ESPAÇO")

                    pressionar_espaco()

                    ultimo_disparo = agora

        time.sleep(0.005)


except KeyboardInterrupt:

    print("\nEncerrado.")


finally:

    try:
        device.close()
    except:
        pass