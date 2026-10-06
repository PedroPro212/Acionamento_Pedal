import ctypes
import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import sys

import hid

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

# ============================================================
# FS-01 / LinTx
# ============================================================
VID = 0x8088
PID = 0x0015
USAGE_PAGE = 0xFF00
PACOTE_PEDAL = [0x66, 0xCC, 0x03, 0x00, 0x01]
INTERVALO_MINIMO = 0.30
TEMPO_RECONEXAO = 2.0

# Windows - Espaço
VK_SPACE = 0x20
KEYEVENTF_KEYUP = 0x0002

# ============================================================
# ARQUIVOS / CORES
# ============================================================
def pasta_app():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent

BASE = pasta_app()
LOGO_FLASH = BASE / "logoFlash.png"
LOGO_PROGRAMACAO = BASE / "logoProgramacaoDiaria.png"

BG = "#0b0d10"
CARD = "#14181d"
CARD_2 = "#101419"
BORDER = "#262c34"
TEXT = "#f4f6f8"
MUTED = "#8e98a5"
RED = "#ff4438"
RED_DARK = "#c62f28"
GREEN = "#2dd4a8"
YELLOW = "#f4c95d"

def pressionar_espaco():
    ctypes.windll.user32.keybd_event(VK_SPACE, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(VK_SPACE, 0, KEYEVENTF_KEYUP, 0)

def localizar_pedal():
    for dispositivo in hid.enumerate(VID, PID):
        if dispositivo.get("usage_page") == USAGE_PAGE:
            return dispositivo
    return None

class FS01App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FS-01 • Disparador da Câmera")
        self.geometry("980x680")
        self.minsize(900, 620)
        self.configure(bg=BG)

        self.eventos = queue.Queue()
        self.parar = threading.Event()
        self.monitorando = False
        self.total_disparos = 0
        self._imagens = []

        self.status_var = tk.StringVar(value="INICIANDO")
        self.status_detalhe = tk.StringVar(value="Procurando o pedal FS-01...")
        self.produto_var = tk.StringVar(value="-")
        self.serial_var = tk.StringVar(value="-")
        self.ultimo_var = tk.StringVar(value="Nenhum")
        self.contador_var = tk.StringVar(value="0")

        self._criar_interface()
        self.protocol("WM_DELETE_WINDOW", self.fechar)
        self.after(100, self.processar_eventos)
        self.iniciar_monitoramento()

    def _logo(self, parent, arquivo, tamanho, bg):
        if Image is None or not arquivo.exists():
            return None
        img = Image.open(arquivo).convert("RGBA")
        img.thumbnail(tamanho, Image.Resampling.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        self._imagens.append(foto)
        lbl = tk.Label(parent, image=foto, bg=bg, bd=0)
        return lbl

    def _botao(self, parent, texto, comando, destaque=False):
        return tk.Button(
            parent, text=texto, command=comando,
            bg=RED if destaque else CARD_2,
            fg="white", activebackground=RED_DARK if destaque else BORDER,
            activeforeground="white", relief="flat", bd=0,
            padx=18, pady=10, cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            highlightthickness=1,
            highlightbackground=RED if destaque else BORDER
        )

    def _card_info(self, parent, titulo, variavel):
        card = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        tk.Label(card, text=titulo.upper(), bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=(13, 3))
        tk.Label(card, textvariable=variavel, bg=CARD, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=15, pady=(0, 13))
        return card

    def _criar_interface(self):
        # Cabeçalho
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=26, pady=(20, 12))

        esquerda = tk.Frame(header, bg=BG)
        esquerda.pack(side="left", fill="y")

        logo = self._logo(esquerda, LOGO_FLASH, (180, 74), BG)
        if logo:
            logo.pack(side="left", padx=(0, 18))

        titulos = tk.Frame(esquerda, bg=BG)
        titulos.pack(side="left", anchor="center")
        tk.Label(titulos, text="DISPARADOR FS-01", bg=BG, fg=TEXT,
                 font=("Segoe UI", 21, "bold")).pack(anchor="w")
        tk.Label(titulos, text="Controle de captura por pedal USB",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))

        logo2 = self._logo(header, LOGO_PROGRAMACAO, (125, 72), BG)
        if logo2:
            logo2.pack(side="right")

        # Linha de destaque
        tk.Frame(self, bg=RED, height=3).pack(fill="x", padx=26, pady=(0, 16))

        # Status principal
        status = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        status.pack(fill="x", padx=26)

        self.status_led = tk.Canvas(status, width=18, height=18, bg=CARD, highlightthickness=0)
        self.status_led.pack(side="left", padx=(18, 10), pady=18)
        self.led = self.status_led.create_oval(3, 3, 15, 15, fill=YELLOW, outline="")

        status_text = tk.Frame(status, bg=CARD)
        status_text.pack(side="left", fill="x", expand=True, pady=12)
        self.status_label = tk.Label(status_text, textvariable=self.status_var, bg=CARD,
                                     fg=YELLOW, font=("Segoe UI", 12, "bold"))
        self.status_label.pack(anchor="w")
        tk.Label(status_text, textvariable=self.status_detalhe, bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        self.btn_monitorar = self._botao(status, "PARAR MONITORAMENTO",
                                         self.alternar_monitoramento, destaque=True)
        self.btn_monitorar.pack(side="right", padx=16)

        # Cards
        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", padx=26, pady=14)
        for c in range(4):
            cards.grid_columnconfigure(c, weight=1, uniform="cards")

        self._card_info(cards, "Produto", self.produto_var).grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        self._card_info(cards, "Serial", self.serial_var).grid(row=0, column=1, sticky="nsew", padx=7)
        self._card_info(cards, "Último disparo", self.ultimo_var).grid(row=0, column=2, sticky="nsew", padx=7)

        contador = tk.Frame(cards, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        contador.grid(row=0, column=3, sticky="nsew", padx=(7, 0))
        tk.Label(contador, text="DISPAROS", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=(11, 0))
        tk.Label(contador, textvariable=self.contador_var, bg=CARD, fg=RED,
                 font=("Segoe UI", 27, "bold")).pack(anchor="w", padx=15, pady=(0, 8))

        # Ações
        acoes = tk.Frame(self, bg=BG)
        acoes.pack(fill="x", padx=26, pady=(0, 12))
        self._botao(acoes, "TESTAR ESPAÇO", self.testar_espaco).pack(side="left")
        self._botao(acoes, "LIMPAR LOG", self.limpar_log).pack(side="left", padx=8)

        # Log
        painel = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        painel.pack(fill="both", expand=True, padx=26, pady=(0, 12))

        cab_log = tk.Frame(painel, bg=CARD)
        cab_log.pack(fill="x", padx=14, pady=(12, 8))
        tk.Label(cab_log, text="ATIVIDADE", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(cab_log, text="eventos HID em tempo real", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=10)

        log_area = tk.Frame(painel, bg=CARD)
        log_area.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.log = tk.Text(log_area, bg=CARD_2, fg="#d9dee5", insertbackground="white",
                           selectbackground=RED_DARK, relief="flat", bd=0,
                           font=("Consolas", 9), state="disabled", wrap="word",
                           padx=12, pady=10)
        scroll = tk.Scrollbar(log_area, command=self.log.yview, bg=CARD)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Rodapé
        footer = tk.Frame(self, bg=BG)
        footer.pack(fill="x", padx=26, pady=(0, 15))
        tk.Label(footer, text="Flash Informática", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(footer, text="FS-01  •  VID 8088  •  PID 0015",
                 bg=BG, fg="#5f6975", font=("Consolas", 8)).pack(side="right")

    def definir_status(self, titulo, detalhe, cor):
        self.status_var.set(titulo)
        self.status_detalhe.set(detalhe)
        self.status_label.configure(fg=cor)
        self.status_led.itemconfig(self.led, fill=cor)

    def adicionar_log(self, mensagem):
        horario = time.strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"[{horario}]  {mensagem}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def limpar_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def testar_espaco(self):
        pressionar_espaco()
        self.adicionar_log("Teste manual -> ESPAÇO enviado.")

    def iniciar_monitoramento(self):
        if self.monitorando:
            return
        self.monitorando = True
        self.parar.clear()
        self.btn_monitorar.configure(text="PARAR MONITORAMENTO")
        threading.Thread(target=self.worker, daemon=True).start()

    def parar_monitoramento(self):
        self.monitorando = False
        self.parar.set()
        self.definir_status("MONITORAMENTO PARADO", "Clique em iniciar para continuar.", MUTED)
        self.btn_monitorar.configure(text="INICIAR MONITORAMENTO")
        self.adicionar_log("Monitoramento interrompido.")

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

                device = hid.device()
                device.open_path(pedal["path"])
                device.set_nonblocking(True)
                self.eventos.put(("conectado", pedal))
                ultimo_disparo = 0

                while not self.parar.is_set():
                    try:
                        dados = device.read(64)
                    except Exception as erro:
                        self.eventos.put(("erro", f"Leitura HID: {erro}"))
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
                if device:
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
                    self.definir_status("PEDAL DESCONECTADO", "Tentando reconectar automaticamente...", RED)
                    self.produto_var.set("-")
                    self.serial_var.set("-")

                elif tipo == "conectado":
                    self.definir_status("PEDAL CONECTADO", "Aguardando acionamento do FS-01.", GREEN)
                    self.produto_var.set(dados.get("product_string") or "LinTx HID Device")
                    self.serial_var.set(dados.get("serial_number") or "-")
                    self.adicionar_log(f"FS-01 conectado | VID={VID:04X} PID={PID:04X} FF00")

                elif tipo == "disparo":
                    self.total_disparos += 1
                    self.contador_var.set(str(self.total_disparos))
                    self.ultimo_var.set(time.strftime("%H:%M:%S"))
                    pacote = " ".join(f"{b:02X}" for b in dados)
                    self.definir_status("DISPARO REALIZADO", "Pedal detectado • tecla Espaço enviada.", GREEN)
                    self.adicionar_log(f"PEDAL -> ESPAÇO | {pacote}")

                elif tipo == "erro":
                    self.definir_status("ERRO DE COMUNICAÇÃO", "Tentando restabelecer a conexão...", RED)
                    self.adicionar_log(f"ERRO: {dados}")

                elif tipo == "parado":
                    self.definir_status("MONITORAMENTO PARADO", "O pedal não está sendo monitorado.", MUTED)

        except queue.Empty:
            pass

        try:
            self.after(100, self.processar_eventos)
        except tk.TclError:
            pass

    def fechar(self):
        self.parar.set()
        self.destroy()

if __name__ == "__main__":
    FS01App().mainloop()
