import ctypes
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

import hid

# ============================================================
# CONFIGURAÇÃO DO FS-01 / LinTx
# ============================================================
VID = 0x8088
PID = 0x0015
USAGE_PAGE = 0xFF00
PACOTE_PEDAL = [0x66, 0xCC, 0x03, 0x00, 0x01]
INTERVALO_MINIMO = 0.30
TEMPO_RECONEXAO = 2.0

# ============================================================
# WINDOWS - TECLA ESPAÇO
# ============================================================
VK_SPACE = 0x20
KEYEVENTF_KEYUP = 0x0002

def pressionar_espaco():
    """Envia uma pulsação da tecla Espaço para a janela ativa do Windows."""
    ctypes.windll.user32.keybd_event(VK_SPACE, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(VK_SPACE, 0, KEYEVENTF_KEYUP, 0)

def localizar_pedal():
    """Localiza a interface proprietária FF00 do FS-01."""
    for dispositivo in hid.enumerate(VID, PID):
        if dispositivo.get("usage_page") == USAGE_PAGE:
            return dispositivo
    return None

class FS01App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FS-01 - Disparador da Câmera")
        self.geometry("760x520")
        self.minsize(680, 460)

        self.eventos = queue.Queue()
        self.parar = threading.Event()
        self.monitorando = False
        self.total_disparos = 0

        self.status_var = tk.StringVar(value="Iniciando...")
        self.produto_var = tk.StringVar(value="-")
        self.serial_var = tk.StringVar(value="-")
        self.ultimo_var = tk.StringVar(value="Nenhum")
        self.contador_var = tk.StringVar(value="0")

        self._criar_interface()
        self.protocol("WM_DELETE_WINDOW", self.fechar)

        self.after(100, self.processar_eventos)
        self.iniciar_monitoramento()

    def _criar_interface(self):
        topo = ttk.Frame(self, padding=16)
        topo.pack(fill="x")

        ttk.Label(
            topo, text="FS-01 • Disparador da Câmera",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")
        ttk.Label(
            topo,
            text="Monitora o pedal LinTx e envia Espaço ao Windows a cada acionamento."
        ).pack(anchor="w", pady=(4, 0))

        info = ttk.LabelFrame(self, text="Estado do dispositivo", padding=12)
        info.pack(fill="x", padx=16, pady=(0, 10))

        campos = [
            ("Status:", self.status_var),
            ("Produto:", self.produto_var),
            ("Serial:", self.serial_var),
            ("Último evento:", self.ultimo_var),
            ("Total de disparos:", self.contador_var),
        ]
        for linha, (rotulo, variavel) in enumerate(campos):
            ttk.Label(info, text=rotulo, font=("Segoe UI", 10, "bold")).grid(
                row=linha, column=0, sticky="w", padx=(0, 12), pady=3
            )
            ttk.Label(info, textvariable=variavel).grid(
                row=linha, column=1, sticky="w", pady=3
            )
        info.columnconfigure(1, weight=1)

        botoes = ttk.Frame(self, padding=(16, 0))
        botoes.pack(fill="x")

        self.btn_monitorar = ttk.Button(
            botoes, text="Parar monitoramento", command=self.alternar_monitoramento
        )
        self.btn_monitorar.pack(side="left")

        ttk.Button(
            botoes, text="Testar Espaço", command=self.testar_espaco
        ).pack(side="left", padx=8)

        ttk.Button(
            botoes, text="Limpar log", command=self.limpar_log
        ).pack(side="left")

        log_frame = ttk.LabelFrame(self, text="Log", padding=8)
        log_frame.pack(fill="both", expand=True, padx=16, pady=12)

        self.log = tk.Text(
            log_frame, height=12, state="disabled",
            font=("Consolas", 9), wrap="word"
        )
        barra = ttk.Scrollbar(log_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=barra.set)
        self.log.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        rodape = ttk.Label(
            self,
            text="Observação: a tecla Espaço é enviada para a janela que estiver ativa no Windows.",
            padding=(16, 0, 16, 12)
        )
        rodape.pack(fill="x")

    def adicionar_log(self, mensagem):
        horario = time.strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"[{horario}] {mensagem}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def limpar_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def testar_espaco(self):
        pressionar_espaco()
        self.adicionar_log("Teste manual: tecla Espaço enviada.")

    def iniciar_monitoramento(self):
        if self.monitorando:
            return
        self.monitorando = True
        self.parar.clear()
        self.btn_monitorar.configure(text="Parar monitoramento")
        threading.Thread(target=self.worker, daemon=True).start()

    def parar_monitoramento(self):
        self.monitorando = False
        self.parar.set()
        self.status_var.set("Monitoramento parado")
        self.btn_monitorar.configure(text="Iniciar monitoramento")
        self.adicionar_log("Monitoramento interrompido pelo usuário.")

    def alternar_monitoramento(self):
        if self.monitorando:
            self.parar_monitoramento()
        else:
            self.iniciar_monitoramento()

    def worker(self):
        device = None

        while not self.parar.is_set():
            try:
                pedal = localizar_pedal()

                if pedal is None:
                    self.eventos.put(("desconectado", None))
                    self.parar.wait(TEMPO_RECONEXAO)
                    continue

                self.eventos.put(("conectando", pedal))

                device = hid.device()
                device.open_path(pedal["path"])
                device.set_nonblocking(True)
                self.eventos.put(("conectado", pedal))

                ultimo_disparo = 0

                while not self.parar.is_set():
                    try:
                        dados = device.read(64)
                    except Exception as erro:
                        self.eventos.put(("erro", f"Leitura HID interrompida: {erro}"))
                        break

                    if dados and dados[:5] == PACOTE_PEDAL:
                        agora = time.time()
                        if agora - ultimo_disparo >= INTERVALO_MINIMO:
                            pressionar_espaco()
                            ultimo_disparo = agora
                            self.eventos.put(("disparo", dados[:5]))

                    time.sleep(0.005)

            except Exception as erro:
                self.eventos.put(("erro", str(erro)))

            finally:
                if device is not None:
                    try:
                        device.close()
                    except Exception:
                        pass
                    device = None

            if not self.parar.is_set():
                self.parar.wait(TEMPO_RECONEXAO)

        self.eventos.put(("parado", None))

    def processar_eventos(self):
        try:
            while True:
                tipo, dados = self.eventos.get_nowait()

                if tipo == "desconectado":
                    self.status_var.set("FS-01 não encontrado • tentando reconectar")
                    self.produto_var.set("-")
                    self.serial_var.set("-")

                elif tipo == "conectando":
                    self.status_var.set("Conectando...")

                elif tipo == "conectado":
                    self.status_var.set("Conectado e aguardando pedal")
                    self.produto_var.set(dados.get("product_string") or "LinTx HID Device")
                    self.serial_var.set(dados.get("serial_number") or "-")
                    self.adicionar_log(
                        f"FS-01 conectado. VID={VID:04X} PID={PID:04X} UsagePage={USAGE_PAGE:04X}"
                    )

                elif tipo == "disparo":
                    self.total_disparos += 1
                    self.contador_var.set(str(self.total_disparos))
                    pacote = " ".join(f"{b:02X}" for b in dados)
                    self.ultimo_var.set(time.strftime("%H:%M:%S"))
                    self.status_var.set("Disparo detectado • Espaço enviado")
                    self.adicionar_log(f"PEDAL -> ESPAÇO | pacote: {pacote}")

                elif tipo == "erro":
                    self.status_var.set("Erro • tentando reconectar")
                    self.adicionar_log(f"ERRO: {dados}")

                elif tipo == "parado":
                    self.status_var.set("Monitoramento parado")

        except queue.Empty:
            pass

        if self.winfo_exists():
            self.after(100, self.processar_eventos)

    def fechar(self):
        self.parar.set()
        self.destroy()

if __name__ == "__main__":
    app = FS01App()
    app.mainloop()
