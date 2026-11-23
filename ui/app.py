"""Ventana principal de la aplicación."""

import tkinter as tk
import traceback

import customtkinter as ctk

from .componentes import (
    FONDO, RUTA_LOGO, SEGMENTO_INACTIVO, TEXTO, TEXTO_TENUE, VERDE_UVG, VERDE_UVG_OSCURO,
    BarraEstado, cargar_logo, configurar_estilo_tablas, fuente,
)
from .vistas import VistaComprobaciones, VistaDesencriptar, VistaEncriptar

PESTANA_ENCRIPTAR = "  Encriptar  "
PESTANA_DESENCRIPTAR = "  Desencriptar  "
PESTANA_COMPROBACIONES = "  Comprobaciones  "


class AplicacionRSA(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("light")
        super().__init__(fg_color=FONDO)
        self.title("Criptografía RSA")
        self.geometry("1280x800")
        self.minsize(1120, 720)
        self.after(300, self._colocar_icono)
        configurar_estilo_tablas()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._construir_encabezado()

        self.barra = BarraEstado(self)
        self.barra.grid(row=2, column=0, sticky="ew")

        self.pestanas = ctk.CTkTabview(self, fg_color="transparent", anchor="nw",
                                       segmented_button_selected_color=VERDE_UVG,
                                       segmented_button_selected_hover_color=VERDE_UVG_OSCURO,
                                       segmented_button_unselected_color=SEGMENTO_INACTIVO,
                                       segmented_button_fg_color=SEGMENTO_INACTIVO)
        self.pestanas.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 12))
        self.pestanas._segmented_button.configure(font=fuente(14, "bold"), height=36)

        contenedores = [self.pestanas.add(nombre) for nombre in
                        (PESTANA_ENCRIPTAR, PESTANA_DESENCRIPTAR, PESTANA_COMPROBACIONES)]
        for contenedor in contenedores:
            contenedor.grid_columnconfigure(0, weight=1)
            contenedor.grid_rowconfigure(0, weight=1)

        self.vista_desencriptar = VistaDesencriptar(contenedores[1], self.barra)
        self.vista_encriptar = VistaEncriptar(contenedores[0], self.barra,
                                              self._usar_en_desencriptar)
        self.vista_comprobaciones = VistaComprobaciones(contenedores[2], self.barra)
        for vista in (self.vista_encriptar, self.vista_desencriptar, self.vista_comprobaciones):
            vista.grid(row=0, column=0, sticky="nsew", pady=(6, 0))

        self.after(100, self.vista_encriptar.entrada_mensaje.focus_set)

    def _construir_encabezado(self):
        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 6))
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(encabezado, text="", image=cargar_logo(56)).grid(
            row=0, column=0, rowspan=2, padx=(0, 14))
        ctk.CTkLabel(encabezado, text="Criptografía RSA", font=fuente(22, "bold"),
                     text_color=TEXTO, anchor="w").grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(encabezado, text="MM2015 Matemática Discreta 1", font=fuente(13),
                     text_color=TEXTO_TENUE, anchor="w").grid(row=1, column=1, sticky="nw")

    def _colocar_icono(self):
        self._icono = tk.PhotoImage(file=RUTA_LOGO)
        self.iconphoto(True, self._icono)

    def _usar_en_desencriptar(self, cifrado, longitud, p, q, e):
        self.vista_desencriptar.recibir(cifrado, longitud, p, q, e)
        self.pestanas.set(PESTANA_DESENCRIPTAR)
        self.barra.mostrar("Datos listos para desencriptar", "exito")

    def report_callback_exception(self, tipo, valor, rastreo):
        """Informa errores inesperados en la barra de estado sin cerrar la aplicación."""
        traceback.print_exception(tipo, valor, rastreo)
        self.barra.mostrar(f"Error inesperado: {valor}", "error")
