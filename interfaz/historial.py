import tkinter as tk

from interfaz.componentes import PanelDesplazable, TarjetaSeleccionable, limpiar, mensaje
from interfaz.tema import BORDE, PRIMARIO_OSCURO, SUPERFICIE, TEXTO, TEXTO_SUAVE, color_por_valor, fuente
from interfaz.vista_reporte import ANGOSTA, mostrar_reporte
from nucleo.almacen import listar_reportes

ANCHO_LISTA = 280


def tarjeta_reporte(padre, reporte, al_hacer_clic):
    tarjeta = TarjetaSeleccionable(padre, al_hacer_clic)
    tarjeta.reporte = reporte
    contenido = tk.Frame(tarjeta.interior, bg=SUPERFICIE)
    contenido.pack(fill="x", padx=10, pady=8)

    color = color_por_valor(reporte["puntuacion"])
    puntuacion = tk.Frame(contenido, bg=color, width=42, height=32)
    puntuacion.pack(side="left", padx=(0, 10))
    puntuacion.pack_propagate(False)
    tk.Label(puntuacion, text=str(reporte["puntuacion"]), font=fuente(12, "bold"), bg=color, fg=TEXTO).place(
        relx=0.5, rely=0.5, anchor="center")

    info = tk.Frame(contenido, bg=SUPERFICIE)
    info.pack(side="left", fill="x", expand=True)
    tk.Label(info, text=reporte["sesion"], font=fuente(10, "bold"), bg=SUPERFICIE, fg=TEXTO).pack(anchor="w")
    tk.Label(info, text=reporte["fecha"], font=fuente(8), bg=SUPERFICIE, fg=TEXTO_SUAVE).pack(anchor="w")

    tarjeta.activar_clic(sin_repintar=[puntuacion])
    return tarjeta


class PestanaHistorial(tk.Frame):
    def __init__(self, padre, bg=SUPERFICIE):
        super().__init__(padre, bg=bg)
        self.tarjeta_activa = None

        cabecera = tk.Frame(self, bg=bg)
        cabecera.pack(fill="x", padx=20, pady=(20, 12))
        tk.Label(cabecera, text="Historial de análisis", font=fuente(13, "bold"), bg=bg, fg=TEXTO).pack(side="left")
        actualizar = tk.Label(cabecera, text="↻  Actualizar", font=fuente(9, "bold"), bg=bg,
                              fg=PRIMARIO_OSCURO, cursor="hand2")
        actualizar.pack(side="right")
        actualizar.bind("<Button-1>", lambda _evento: self.recargar())

        cuerpo = tk.Frame(self, bg=bg)
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.lista = PanelDesplazable(cuerpo, bg=bg, width=ANCHO_LISTA)
        self.lista.pack(side="left", fill="y", padx=(0, 16))
        self.lista.pack_propagate(False)

        marco = tk.Frame(cuerpo, bg=BORDE)
        marco.pack(side="left", fill="both", expand=True)
        self.detalle = PanelDesplazable(marco, bg=bg)
        self.detalle.pack(fill="both", expand=True, padx=1, pady=1)

        self.recargar()

    def recargar(self):
        limpiar(self.lista.interior)
        limpiar(self.detalle.interior)
        self.tarjeta_activa = None

        reportes = listar_reportes()
        if not reportes:
            mensaje(self.lista.interior, "Aún no hay reportes guardados.\n\nAnaliza un audio o un texto\n"
                                         "para comenzar.")
            return
        for reporte in reportes:
            tarjeta_reporte(self.lista.interior, reporte, self._seleccionar).pack(fill="x", pady=3)
        mensaje(self.detalle.interior, "Selecciona un reporte de la lista para ver su detalle.")

    def _seleccionar(self, tarjeta):
        if self.tarjeta_activa is not None:
            self.tarjeta_activa.seleccionar(False)
        tarjeta.seleccionar(True)
        self.tarjeta_activa = tarjeta
        mostrar_reporte(self.detalle.interior, tarjeta.reporte, ANGOSTA)
        self.detalle.al_inicio()
