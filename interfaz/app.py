import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from config import EXTENSIONES_AUDIO
from interfaz.componentes import BotonPlano, PanelDesplazable, limpiar, mensaje
from interfaz.historial import PestanaHistorial
from interfaz.tema import (
    BORDE,
    FONDO,
    GRABANDO,
    GRABAR,
    PRIMARIO,
    PRIMARIO_OSCURO,
    SECUNDARIO,
    SUPERFICIE,
    TEXTO,
    TEXTO_SUAVE,
    fuente,
)
from interfaz.vista_reporte import mostrar_reporte
from nucleo import flujo
from nucleo.grabador import Grabador, MicrofonoNoDisponible
from nucleo.transcriptor import Transcriptor

TITULO = "EXPRESA"
TAMANO_VENTANA = "1000x780"
MINIMO_PALABRAS_TEXTO = 5
MILISEGUNDOS_CRONOMETRO = 1000


class Aplicacion:
    def __init__(self):
        self.raiz = tk.Tk()
        self.raiz.title(TITULO)
        self.raiz.geometry(TAMANO_VENTANA)
        self.raiz.configure(bg=FONDO)
        self._configurar_estilos()

        self.grabador = Grabador()
        self.transcriptor = Transcriptor()
        self.ruta_audio = None
        self.inicio_grabacion = 0
        self.cronometro = None
        self.ocupado = False

        self._construir()

    def ejecutar(self):
        self.raiz.mainloop()

    def _configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("TNotebook", background=FONDO, borderwidth=0)
        estilo.configure("TNotebook.Tab", background=SECUNDARIO, foreground=TEXTO,
                         padding=[22, 10], font=fuente(10, "bold"), borderwidth=0)
        estilo.map("TNotebook.Tab", background=[("selected", PRIMARIO)])

    def _construir(self):
        cabecera = tk.Frame(self.raiz, bg=FONDO)
        cabecera.pack(fill="x", padx=30, pady=(20, 4))
        tk.Label(cabecera, text=TITULO, font=fuente(22, "bold"), bg=FONDO, fg=TEXTO).pack(anchor="w")
        tk.Label(cabecera, text="Análisis de comunicación oral y escrita", font=fuente(11, "bold"),
                 bg=FONDO, fg=PRIMARIO_OSCURO).pack(anchor="w")
        self.estado = tk.Label(cabecera, text="", font=fuente(10), bg=FONDO, fg=TEXTO_SUAVE)
        self.estado.pack(anchor="w", pady=(6, 0))

        self.pestanas = ttk.Notebook(self.raiz)
        self.pestanas.pack(fill="both", expand=True, padx=30, pady=(6, 20))
        self.resultados_audio = self._pestana_audio()
        self.resultados_texto = self._pestana_texto()
        self.historial = PestanaHistorial(self.pestanas)
        self.pestanas.add(self.historial, text="Historial")

    def _nueva_pestana(self, titulo, instruccion):
        pestana = tk.Frame(self.pestanas, bg=SUPERFICIE)
        self.pestanas.add(pestana, text=titulo)
        contenido = tk.Frame(pestana, bg=SUPERFICIE)
        contenido.pack(fill="both", expand=True, padx=30, pady=24)
        tk.Label(contenido, text=instruccion, font=fuente(13, "bold"), bg=SUPERFICIE,
                 fg=PRIMARIO_OSCURO).pack(anchor="w", pady=(0, 12))
        return contenido

    def _panel_resultados(self, contenedor):
        marco = tk.Frame(contenedor, bg=BORDE)
        marco.pack(fill="both", expand=True, pady=(14, 0))
        panel = PanelDesplazable(marco)
        panel.pack(fill="both", expand=True, padx=1, pady=1)
        mensaje(panel.interior, "Aún no hay un análisis para mostrar.")
        return panel

    def _pestana_audio(self):
        contenido = self._nueva_pestana("Análisis de audio", "Graba tu voz o selecciona un archivo de audio")
        botones = tk.Frame(contenido, bg=SUPERFICIE)
        botones.pack(anchor="w", fill="x")
        self.boton_grabar = BotonPlano(botones, "Iniciar grabación", self._alternar_grabacion, bg=GRABAR)
        self.boton_grabar.pack(side="left", padx=(0, 10))
        BotonPlano(botones, "Seleccionar archivo", self._seleccionar_archivo, bg=SECUNDARIO).pack(side="left")
        BotonPlano(botones, "Analizar audio", self._analizar_audio).pack(side="right")

        self.estado_audio = tk.Label(contenido, text="Ningún audio seleccionado", font=fuente(10, "bold"),
                                     bg=SUPERFICIE, fg=TEXTO_SUAVE)
        self.estado_audio.pack(anchor="w", pady=(12, 0))
        return self._panel_resultados(contenido)

    def _pestana_texto(self):
        contenido = self._nueva_pestana("Análisis de texto", "Escribe o pega el texto a analizar")
        marco = tk.Frame(contenido, bg=SECUNDARIO)
        marco.pack(fill="x")
        self.entrada_texto = tk.Text(marco, height=6, bg=FONDO, fg=TEXTO, font=fuente(11), relief="flat",
                                     padx=15, pady=15, bd=0, wrap="word")
        self.entrada_texto.pack(fill="both", expand=True, padx=2, pady=2)
        BotonPlano(contenido, "Analizar texto", self._analizar_texto).pack(anchor="w", pady=(12, 0))
        return self._panel_resultados(contenido)

    def _alternar_grabacion(self):
        if self.grabador.grabando:
            self._detener_grabacion()
        else:
            self._iniciar_grabacion()

    def _iniciar_grabacion(self):
        try:
            self.grabador.verificar_microfono()
        except MicrofonoNoDisponible as error:
            messagebox.showerror("Micrófono", str(error))
            return
        self.inicio_grabacion = time.monotonic()
        self.grabador.iniciar()
        self.boton_grabar.cambiar("Detener grabación", GRABANDO)
        self._actualizar_cronometro()

    def _detener_grabacion(self):
        if self.cronometro:
            self.raiz.after_cancel(self.cronometro)
        self.ruta_audio = self.grabador.detener()
        self.boton_grabar.cambiar("Iniciar grabación", GRABAR)
        if self.ruta_audio is None:
            self.estado_audio.config(text="No se captó audio, intenta de nuevo", fg=GRABANDO)
            return
        self.estado_audio.config(text=f"Grabación lista ({self.grabador.duracion:.0f} s)", fg=PRIMARIO_OSCURO)

    def _actualizar_cronometro(self):
        segundos = int(time.monotonic() - self.inicio_grabacion)
        self.estado_audio.config(text=f"Grabando... {segundos // 60:02d}:{segundos % 60:02d}", fg=GRABANDO)
        self.cronometro = self.raiz.after(MILISEGUNDOS_CRONOMETRO, self._actualizar_cronometro)

    def _seleccionar_archivo(self):
        patrones = " ".join(f"*{extension}" for extension in EXTENSIONES_AUDIO)
        ruta = filedialog.askopenfilename(filetypes=[("Audio", patrones)])
        if ruta:
            self.ruta_audio = Path(ruta)
            self.estado_audio.config(text=f"Archivo seleccionado: {self.ruta_audio.name}", fg=PRIMARIO_OSCURO)

    def _analizar_audio(self):
        if self.grabador.grabando:
            messagebox.showwarning("Atención", "Detén la grabación antes de analizar.")
            return
        if self.ruta_audio is None:
            messagebox.showwarning("Atención", "Graba o selecciona un audio primero.")
            return
        ruta = self.ruta_audio
        self._en_segundo_plano(
            lambda: flujo.analizar_audio(ruta, self.transcriptor, aviso=self._avisar),
            self.resultados_audio,
        )

    def _analizar_texto(self):
        texto = self.entrada_texto.get("1.0", "end").strip()
        if len(texto.split()) < MINIMO_PALABRAS_TEXTO:
            messagebox.showwarning("Atención", f"Ingresa al menos {MINIMO_PALABRAS_TEXTO} palabras.")
            return
        self._en_segundo_plano(lambda: flujo.analizar_texto(texto), self.resultados_texto)

    # Desde el hilo de trabajo solo se toca la ventana a traves de after()
    def _avisar(self, texto):
        self.raiz.after(0, lambda: self.estado.config(text=texto, fg=PRIMARIO_OSCURO))

    def _en_segundo_plano(self, tarea, panel):
        if self.ocupado:
            messagebox.showinfo("Espera", "Ya hay un análisis en curso.")
            return
        self.ocupado = True
        limpiar(panel.interior)
        mensaje(panel.interior, "Analizando, esto puede tardar unos segundos...")
        self._avisar("Procesando el análisis...")

        def trabajar():
            try:
                reporte = tarea()
            except Exception as error:
                # Python borra 'error' al salir del except, por eso se pasa como argumento
                self.raiz.after(0, lambda fallo=error: self._terminar_con_error(fallo, panel))
                return
            self.raiz.after(0, lambda: self._terminar(reporte, panel))

        threading.Thread(target=trabajar, daemon=True).start()

    def _terminar(self, reporte, panel):
        self.ocupado = False
        mostrar_reporte(panel.interior, reporte)
        panel.al_inicio()
        self.estado.config(text="Análisis completado y guardado en el historial.", fg=TEXTO_SUAVE)
        self.historial.recargar()

    def _terminar_con_error(self, error, panel):
        self.ocupado = False
        limpiar(panel.interior)
        mensaje(panel.interior, "No se pudo completar el análisis.")
        self.estado.config(text="", fg=TEXTO_SUAVE)
        messagebox.showerror("Error", str(error))
