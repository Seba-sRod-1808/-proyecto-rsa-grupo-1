"""Componentes visuales reutilizables y paleta de colores de la aplicación."""

import os
import sys
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk
from PIL import Image

from rsa_core import ErrorValidacion, validar_parametros

RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_LOGO = os.path.join(RAIZ_PROYECTO, "assets", "logo_uvg.png")

VERDE_UVG = "#0c8c39"
VERDE_UVG_OSCURO = "#0a7330"
VERDE_SUAVE = "#dcf1e3"
FONDO = "#eef2ef"
TARJETA = "#ffffff"
INDICADOR = "#f4f7f5"
BORDE = "#d7dfda"
TEXTO = "#1d2420"
TEXTO_TENUE = "#5f6b64"
SEGMENTO_INACTIVO = "#7d8a82"
EXITO = "#1a7f37"
ERROR = "#c62828"
AVISO = "#9a6700"

if sys.platform.startswith("win"):
    FAMILIA_MONO = "Consolas"
elif sys.platform == "darwin":
    FAMILIA_MONO = "Menlo"
else:
    FAMILIA_MONO = "DejaVu Sans Mono"


def fuente(tamano=13, peso="normal", mono=False):
    if mono:
        return ctk.CTkFont(family=FAMILIA_MONO, size=tamano, weight=peso)
    return ctk.CTkFont(size=tamano, weight=peso)


def cargar_logo(lado):
    return ctk.CTkImage(light_image=Image.open(RUTA_LOGO), size=(lado, lado))


def caracter_visible(caracter):
    return "␣" if caracter == " " else caracter


def escribir_solo_lectura(entrada, texto):
    entrada.configure(state="normal")
    entrada.delete(0, "end")
    entrada.insert(0, texto)
    entrada.configure(state="readonly")


def boton_primario(master, texto, comando, **opciones):
    return ctk.CTkButton(master, text=texto, command=comando, height=42, corner_radius=10,
                         font=fuente(14, "bold"), fg_color=VERDE_UVG,
                         hover_color=VERDE_UVG_OSCURO, **opciones)


def boton_secundario(master, texto, comando, **opciones):
    return ctk.CTkButton(master, text=texto, command=comando, height=34, corner_radius=10,
                         fg_color="transparent", border_width=1, border_color=BORDE,
                         text_color=TEXTO, hover_color=VERDE_SUAVE, font=fuente(13),
                         **opciones)


class Tarjeta(ctk.CTkFrame):
    """Contenedor blanco con borde y título opcional; el contenido va en ``cuerpo``."""

    def __init__(self, master, titulo=None, **opciones):
        super().__init__(master, corner_radius=14, fg_color=TARJETA, border_width=1,
                         border_color=BORDE, **opciones)
        self.grid_columnconfigure(0, weight=1)
        fila_cuerpo = 0
        if titulo:
            ctk.CTkLabel(self, text=titulo, font=fuente(15, "bold"), text_color=TEXTO,
                         anchor="w").grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 0))
            fila_cuerpo = 1
        self.cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.cuerpo.grid(row=fila_cuerpo, column=0, sticky="nsew", padx=18, pady=(10, 16))
        self.grid_rowconfigure(fila_cuerpo, weight=1)


class Indicador(ctk.CTkFrame):
    """Recuadro pequeño con un nombre y un valor calculado."""

    def __init__(self, master, nombre):
        super().__init__(master, corner_radius=10, fg_color=INDICADOR)
        ctk.CTkLabel(self, text=nombre, font=fuente(12), text_color=TEXTO_TENUE,
                     anchor="w").pack(fill="x", padx=12, pady=(8, 0))
        self.valor = ctk.CTkLabel(self, font=fuente(17, "bold", mono=True), anchor="w")
        self.valor.pack(fill="x", padx=12, pady=(0, 8))
        self.reiniciar()

    def mostrar(self, texto, color=TEXTO):
        self.valor.configure(text=texto, text_color=color)

    def reiniciar(self):
        self.mostrar("—", TEXTO_TENUE)


def configurar_estilo_tablas():
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("RSA.Treeview", background=TARJETA, fieldbackground=TARJETA,
                     foreground=TEXTO, rowheight=30, borderwidth=0, font=(FAMILIA_MONO, 11))
    estilo.configure("RSA.Treeview.Heading", background=INDICADOR, foreground=TEXTO,
                     relief="flat", borderwidth=0, font=("TkDefaultFont", 10, "bold"),
                     padding=6)
    estilo.map("RSA.Treeview", background=[("selected", VERDE_SUAVE)],
               foreground=[("selected", TEXTO)])
    estilo.map("RSA.Treeview.Heading", background=[("active", INDICADOR)])
    estilo.layout("RSA.Treeview", [("RSA.Treeview.treearea", {"sticky": "nswe"})])


class Tabla(ctk.CTkFrame):
    """``ttk.Treeview`` con barra de desplazamiento y aviso cuando está vacía.

    Args:
        columnas: lista de tuplas ``(id, encabezado, ancho, alineación)``.
    """

    def __init__(self, master, columnas):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.arbol = ttk.Treeview(self, columns=[c[0] for c in columnas], show="headings",
                                  style="RSA.Treeview", selectmode="browse")
        for identificador, encabezado, ancho, alineacion in columnas:
            self.arbol.heading(identificador, text=encabezado, anchor=alineacion)
            self.arbol.column(identificador, width=ancho, minwidth=40, anchor=alineacion)
        self.arbol.tag_configure("relleno", foreground=AVISO)
        self.arbol.tag_configure("exito", foreground=EXITO)
        self.arbol.tag_configure("error", foreground=ERROR)
        self.arbol.grid(row=0, column=0, sticky="nsew")

        barra = ctk.CTkScrollbar(self, command=self.arbol.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.arbol.configure(yscrollcommand=barra.set)

        self.aviso_vacia = ctk.CTkLabel(self, text="Sin resultados todavía", font=fuente(12),
                                        text_color=TEXTO_TENUE, bg_color=TARJETA)
        self.limpiar()

    def cargar(self, filas):
        """Reemplaza el contenido; cada fila es ``(valores, etiqueta_o_None)``."""
        self.limpiar()
        for valores, etiqueta in filas:
            self.arbol.insert("", "end", values=valores, tags=(etiqueta,) if etiqueta else ())
        if filas:
            self.aviso_vacia.place_forget()

    def limpiar(self):
        self.arbol.delete(*self.arbol.get_children())
        self.aviso_vacia.place(relx=0.5, rely=0.55, anchor="center")


class FormularioParametros(ctk.CTkFrame):
    """Campos p, q y e con validación en vivo de n y φ."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="parametro")
        self.variables = {}
        self.entradas = []
        for columna, nombre in enumerate("pqe"):
            separacion = (0 if columna == 0 else 8, 0)
            ctk.CTkLabel(self, text=nombre, font=fuente(13, "bold"), text_color=TEXTO,
                         anchor="w").grid(row=0, column=columna, sticky="w", padx=separacion)
            variable = tk.StringVar()
            variable.trace_add("write", lambda *_: self._validar_en_vivo())
            entrada = ctk.CTkEntry(self, textvariable=variable, height=36,
                                   font=fuente(14, mono=True))
            entrada.grid(row=1, column=columna, sticky="ew", padx=separacion)
            self.variables[nombre] = variable
            self.entradas.append(entrada)

        self.estado = ctk.CTkLabel(self, text="", font=fuente(12), anchor="w", justify="left",
                                   wraplength=330)
        self.estado.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 0))

    def valores(self):
        return tuple(self.variables[nombre].get() for nombre in "pqe")

    def establecer(self, p, q, e):
        for nombre, valor in zip("pqe", (p, q, e)):
            self.variables[nombre].set(str(valor))

    def limpiar(self):
        self.establecer("", "", "")

    def _validar_en_vivo(self):
        if not any(valor.strip() for valor in self.valores()):
            self.estado.configure(text="")
            return
        try:
            params = validar_parametros(*self.valores())
        except ErrorValidacion as error:
            self.estado.configure(text=str(error), text_color=AVISO)
        else:
            self.estado.configure(text=f"✓  n = {params.n}   ·   φ = {params.phi}",
                                  text_color=EXITO)


class BarraEstado(ctk.CTkFrame):
    """Franja inferior que informa el resultado de la última acción."""

    _ESTILOS = {"info": ("", TEXTO_TENUE), "exito": ("✓   ", EXITO), "error": ("✕   ", ERROR)}

    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color=TARJETA, border_width=1,
                         border_color=BORDE)
        self.texto = ctk.CTkLabel(self, text="", anchor="w", font=fuente(12))
        self.texto.pack(fill="x", padx=16, pady=6)

    def mostrar(self, mensaje, tipo="info"):
        icono, color = self._ESTILOS[tipo]
        self.texto.configure(text=icono + mensaje, text_color=color)
