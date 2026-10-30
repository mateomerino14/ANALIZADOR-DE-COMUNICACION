import sys
import tkinter as tk

from interfaz.tema import (
    BORDE,
    PRIMARIO,
    PRIMARIO_OSCURO,
    SECUNDARIO,
    SELECCION,
    SUPERFICIE,
    TEXTO,
    TEXTO_SUAVE,
    color_por_valor,
    fuente,
)

PASOS_RUEDA_WINDOWS = 120


def limpiar(contenedor):
    for hijo in contenedor.winfo_children():
        hijo.destroy()


def mensaje(contenedor, texto, bg=SUPERFICIE):
    tk.Label(contenedor, text=texto, font=fuente(10), bg=bg, fg=TEXTO_SUAVE, justify="center").pack(pady=40)


class BotonPlano(tk.Label):
    def __init__(self, padre, texto, comando, bg=PRIMARIO, **opciones):
        super().__init__(padre, text=texto, bg=bg, fg=TEXTO, font=fuente(11, "bold"),
                         cursor="hand2", padx=26, pady=11, **opciones)
        self.comando = comando
        self.bind("<Button-1>", lambda _evento: self.comando())

    def cambiar(self, texto, bg):
        self.config(text=texto, bg=bg)


# Frame con barra de desplazamiento que tambien responde a la rueda del mouse
class PanelDesplazable(tk.Frame):
    def __init__(self, padre, bg=SUPERFICIE, **opciones):
        super().__init__(padre, bg=bg, **opciones)
        barra = tk.Scrollbar(self)
        barra.pack(side="right", fill="y")
        self.lienzo = tk.Canvas(self, bg=bg, highlightthickness=0, yscrollcommand=barra.set)
        self.lienzo.pack(side="left", fill="both", expand=True)
        barra.config(command=self.lienzo.yview)

        self.interior = tk.Frame(self.lienzo, bg=bg)
        ventana = self.lienzo.create_window((0, 0), window=self.interior, anchor="nw")
        self.interior.bind("<Configure>",
                           lambda _evento: self.lienzo.configure(scrollregion=self.lienzo.bbox("all")))
        self.lienzo.bind("<Configure>", lambda evento: self.lienzo.itemconfig(ventana, width=evento.width))
        self.bind("<Enter>", self._activar_rueda)
        self.bind("<Leave>", self._desactivar_rueda)

    def _activar_rueda(self, _evento):
        self.bind_all("<MouseWheel>", self._rueda)
        self.bind_all("<Button-4>", lambda _evento: self.lienzo.yview_scroll(-1, "units"))
        self.bind_all("<Button-5>", lambda _evento: self.lienzo.yview_scroll(1, "units"))

    def _desactivar_rueda(self, _evento):
        for secuencia in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.unbind_all(secuencia)

    # En Windows cada paso de la rueda vale 120 y en macOS vale 1
    def _rueda(self, evento):
        pasos = evento.delta
        if sys.platform == "win32":
            pasos = evento.delta // PASOS_RUEDA_WINDOWS
        self.lienzo.yview_scroll(-pasos, "units")

    def al_inicio(self):
        self.lienzo.yview_moveto(0)


def _rectangulo_redondeado(lienzo, x1, y1, x2, y2, radio, **opciones):
    puntos = [
        x1 + radio, y1, x2 - radio, y1, x2, y1, x2, y1 + radio,
        x2, y2 - radio, x2, y2, x2 - radio, y2, x1 + radio, y2,
        x1, y2, x1, y2 - radio, x1, y1 + radio, x1, y1,
    ]
    return lienzo.create_polygon(puntos, smooth=True, **opciones)


class BarraProgreso(tk.Frame):
    def __init__(self, padre, etiqueta, valor, ancho=320, alto=22, bg=SUPERFICIE):
        super().__init__(padre, bg=bg)
        tk.Label(self, text=etiqueta, font=fuente(10), bg=bg, fg=TEXTO, width=14, anchor="w").pack(side="left")
        lienzo = tk.Canvas(self, width=ancho, height=alto, bg=bg, highlightthickness=0)
        lienzo.pack(side="left", padx=(6, 8))
        tk.Label(self, text=f"{valor:.0f}", font=fuente(10, "bold"), bg=bg, fg=PRIMARIO_OSCURO,
                 width=4, anchor="w").pack(side="left")

        valor = max(0, min(valor, 100))
        _rectangulo_redondeado(lienzo, 1, 1, ancho - 1, alto - 1, alto // 2, fill=BORDE, outline="")
        if valor > 0:
            relleno = max(alto, valor / 100 * (ancho - 2) + 1)
            _rectangulo_redondeado(lienzo, 1, 1, relleno, alto - 1, alto // 2,
                                   fill=color_por_valor(valor), outline="")


class Medidor(tk.Frame):
    def __init__(self, padre, valor, nivel, diametro=140, bg=SUPERFICIE):
        super().__init__(padre, bg=bg)
        lienzo = tk.Canvas(self, width=diametro, height=diametro, bg=bg, highlightthickness=0)
        lienzo.pack()
        tk.Label(self, text=nivel, font=fuente(11, "bold"), bg=bg, fg=PRIMARIO_OSCURO).pack(pady=(6, 0))

        grosor = max(10, diametro // 10)
        margen = grosor // 2 + 2
        caja = (margen, margen, diametro - margen, diametro - margen)
        lienzo.create_oval(*caja, outline=BORDE, width=grosor)
        if valor > 0:
            lienzo.create_arc(*caja, start=90, extent=-valor / 100 * 359.9, style="arc",
                              outline=color_por_valor(valor), width=grosor)
        centro = diametro / 2
        lienzo.create_text(centro, centro - 6, text=f"{valor:.0f}",
                           font=fuente(int(diametro * 0.22), "bold"), fill=PRIMARIO_OSCURO)
        lienzo.create_text(centro, centro + diametro * 0.18, text="/ 100",
                           font=fuente(int(diametro * 0.08)), fill=TEXTO_SUAVE)


class TarjetaMetrica(tk.Frame):
    def __init__(self, padre, titulo, valor, descripcion, color, bg=SUPERFICIE, ancho=200):
        super().__init__(padre, bg=BORDE)
        tk.Frame(self, bg=color, width=4).pack(side="left", fill="y")
        contenido = tk.Frame(self, bg=bg)
        contenido.pack(side="left", fill="both", expand=True, padx=(0, 1), pady=1)
        tk.Label(contenido, text=titulo.upper(), font=fuente(8, "bold"), bg=bg, fg=TEXTO_SUAVE).pack(
            anchor="w", padx=14, pady=(10, 0))
        tk.Label(contenido, text=valor, font=fuente(16, "bold"), bg=bg, fg=TEXTO, wraplength=ancho - 28,
                 justify="left").pack(anchor="w", padx=14)
        tk.Label(contenido, text=descripcion, font=fuente(8), bg=bg, fg=TEXTO_SUAVE,
                 wraplength=ancho - 28, justify="left").pack(anchor="w", padx=14, pady=(0, 10))


class EncabezadoSeccion(tk.Frame):
    def __init__(self, padre, titulo, bg=SUPERFICIE):
        super().__init__(padre, bg=bg)
        tk.Label(self, text=titulo, font=fuente(12, "bold"), bg=bg, fg=PRIMARIO_OSCURO).pack(side="left")
        tk.Frame(self, bg=BORDE, height=1).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=(4, 0))


def etiqueta_color(padre, texto, color):
    return tk.Label(padre, text=texto, font=fuente(8, "bold"), bg=color, fg=TEXTO, padx=8, pady=2)


# Cada segmento es (texto, color); sin color se usa el texto normal
def fila_resaltada(padre, segmentos, bg=SUPERFICIE):
    fila = tk.Frame(padre, bg=bg)
    for texto, color in segmentos:
        peso = "bold"
        if color is None:
            peso = "normal"
            color = TEXTO
        tk.Label(fila, text=texto, font=fuente(9, peso), bg=bg, fg=color).pack(side="left")
    return fila


class TarjetaSeleccionable(tk.Frame):
    def __init__(self, padre, al_hacer_clic, bg=SUPERFICIE):
        super().__init__(padre, bg=BORDE, cursor="hand2")
        self.bg_normal = bg
        self.seleccionada = False
        self.sin_repintar = set()
        self.interior = tk.Frame(self, bg=bg, cursor="hand2")
        self.interior.pack(fill="both", expand=True, padx=1, pady=1)
        self.al_hacer_clic = al_hacer_clic
        self.bind("<Enter>", lambda _evento: self._pintar_si_libre(SECUNDARIO))
        self.bind("<Leave>", lambda _evento: self._pintar_si_libre(self.bg_normal))

    # Se llama despues de armar el contenido para que todo el bloque responda al clic
    def activar_clic(self, sin_repintar=()):
        self.sin_repintar = set(sin_repintar)
        for widget in _descendientes(self):
            widget.bind("<Button-1>", lambda _evento: self.al_hacer_clic(self))

    def seleccionar(self, valor):
        self.seleccionada = valor
        if valor:
            self._pintar(SELECCION)
        else:
            self._pintar(self.bg_normal)

    def _pintar_si_libre(self, color):
        if not self.seleccionada:
            self._pintar(color)

    def _pintar(self, color):
        for widget in _descendientes(self.interior, self.sin_repintar):
            widget.config(bg=color)


def _descendientes(widget, omitir=()):
    if widget in omitir:
        return
    yield widget
    for hijo in widget.winfo_children():
        yield from _descendientes(hijo, omitir)
