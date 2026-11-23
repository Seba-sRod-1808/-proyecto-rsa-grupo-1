"""Pestañas de la aplicación: Encriptar, Desencriptar y Comprobaciones."""

import tkinter as tk

import customtkinter as ctk

from rsa_core import ErrorValidacion, desencriptar, encriptar
from rsa_core.comprobaciones import ejecutar_todas
from .componentes import (
    AVISO, BORDE, ERROR, EXITO, FONDO, SEGMENTO_INACTIVO, TARJETA, TEXTO, TEXTO_TENUE,
    VERDE_UVG, VERDE_UVG_OSCURO, BarraEstado, FormularioParametros, Indicador, Tabla,
    Tarjeta, boton_primario, boton_secundario, caracter_visible, escribir_solo_lectura,
    fuente,
)

EJEMPLO_MENSAJE = "RSA"
EJEMPLO_CIFRADO = "026054 123875"
EJEMPLO_L = 3
EJEMPLO_PARAMETROS = (367, 373, 17)
ANCHO_FORMULARIO = 380


def crear_pestanas_detalle(master, *nombres):
    pestanas = ctk.CTkTabview(master, corner_radius=14, fg_color=TARJETA, bg_color=FONDO,
                              border_width=1, border_color=BORDE,
                              segmented_button_selected_color=VERDE_UVG,
                              segmented_button_selected_hover_color=VERDE_UVG_OSCURO,
                              segmented_button_unselected_color=SEGMENTO_INACTIVO,
                              segmented_button_fg_color=SEGMENTO_INACTIVO)
    contenedores = []
    for nombre in nombres:
        contenedor = pestanas.add(nombre)
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_rowconfigure(0, weight=1)
        contenedores.append(contenedor)
    return pestanas, contenedores


def nota_de_caracter(caracter, texto_relleno):
    if caracter.es_relleno:
        return texto_relleno
    return "espacio" if caracter.caracter == " " else ""


class _VistaOperacion(ctk.CTkFrame):
    """Distribución común: formulario a la izquierda y resultados a la derecha."""

    def __init__(self, master, barra: BarraEstado):
        super().__init__(master, fg_color="transparent")
        self.barra = barra
        self.resultado = None
        self.grid_columnconfigure(0, minsize=ANCHO_FORMULARIO)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.formulario = Tarjeta(self, "Datos de entrada", width=ANCHO_FORMULARIO)
        self.formulario.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.formulario.grid_propagate(False)

        self.panel_resultados = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_resultados.grid(row=0, column=1, sticky="nsew")
        self.panel_resultados.grid_columnconfigure(0, weight=1)
        self.panel_resultados.grid_rowconfigure(2, weight=1)

    def _titulo_campo(self, texto, **empaque):
        ctk.CTkLabel(self.formulario.cuerpo, text=texto, font=fuente(13, "bold"),
                     text_color=TEXTO, anchor="w").pack(fill="x", **empaque)

    def _pista(self):
        return ctk.CTkLabel(self.formulario.cuerpo, text="", font=fuente(12), anchor="w",
                            justify="left", wraplength=ANCHO_FORMULARIO - 40)

    def _separador(self):
        ctk.CTkFrame(self.formulario.cuerpo, height=1, fg_color=BORDE).pack(fill="x", pady=14)

    def _acciones(self, texto_principal):
        cuerpo = self.formulario.cuerpo
        self.mensaje_error = ctk.CTkLabel(cuerpo, text="", font=fuente(12), text_color=ERROR,
                                          anchor="w", justify="left",
                                          wraplength=ANCHO_FORMULARIO - 40)
        self.mensaje_error.pack(fill="x", pady=(12, 0))
        boton_primario(cuerpo, texto_principal, self.ejecutar).pack(fill="x", pady=(12, 8))

        fila = ctk.CTkFrame(cuerpo, fg_color="transparent")
        fila.pack(fill="x")
        fila.grid_columnconfigure((0, 1), weight=1)
        boton_secundario(fila, "Cargar ejemplo", self.cargar_ejemplo).grid(
            row=0, column=0, sticky="ew", padx=(0, 4))
        boton_secundario(fila, "Limpiar", self.limpiar).grid(
            row=0, column=1, sticky="ew", padx=(4, 0))

    def _ejecutar_con_enter(self, *entradas):
        for entrada in entradas:
            entrada.bind("<Return>", lambda _: self.ejecutar())

    def _crear_indicadores(self, nombres):
        fila = ctk.CTkFrame(self.panel_resultados, fg_color="transparent")
        fila.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        indicadores = {}
        for columna, (clave, nombre) in enumerate(nombres):
            peso = 2 if clave == "llave" else 1
            fila.grid_columnconfigure(columna, weight=peso, uniform="indicador")
            indicador = Indicador(fila, nombre)
            indicador.grid(row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 8, 0))
            indicadores[clave] = indicador
        return indicadores

    def _copiar(self, texto, nombre):
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.barra.mostrar(f"{nombre} copiado al portapapeles.", "exito")

    def ejecutar(self):
        try:
            self.resultado = self._calcular()
        except ErrorValidacion as error:
            self._mostrar_error(str(error))
            return
        self.mensaje_error.configure(text="")
        self._mostrar_resultado(self.resultado)

    def _mostrar_error(self, mensaje):
        """Borra los resultados previos para que no se confundan con una salida válida."""
        self.limpiar_resultados()
        self.mensaje_error.configure(text=mensaje)
        self.barra.mostrar(mensaje, "error")

    def limpiar_resultados(self):
        self.resultado = None
        for indicador in self.indicadores.values():
            indicador.reiniciar()
        for tabla in self.tablas:
            tabla.limpiar()
        self._limpiar_salida()

    def limpiar(self):
        self._limpiar_formulario()
        self.mensaje_error.configure(text="")
        self.limpiar_resultados()
        self.barra.mostrar("")


class VistaEncriptar(_VistaOperacion):
    def __init__(self, master, barra, al_usar_en_desencriptar):
        super().__init__(master, barra)
        self.al_usar_en_desencriptar = al_usar_en_desencriptar
        self._construir_formulario()
        self._construir_resultados()
        self.limpiar_resultados()

    def _construir_formulario(self):
        self._titulo_campo("Mensaje")
        self.mensaje = tk.StringVar()
        self.mensaje.trace_add("write", lambda *_: self._describir_mensaje())
        self.entrada_mensaje = ctk.CTkEntry(self.formulario.cuerpo, textvariable=self.mensaje,
                                            height=38, font=fuente(14, mono=True))
        self.entrada_mensaje.pack(fill="x", pady=(4, 2))
        self.pista_mensaje = self._pista()
        self.pista_mensaje.pack(fill="x")

        self._separador()
        self.parametros = FormularioParametros(self.formulario.cuerpo)
        self.parametros.pack(fill="x")
        self._acciones("Encriptar")
        self._ejecutar_con_enter(self.entrada_mensaje, *self.parametros.entradas)

    def _describir_mensaje(self):
        mensaje = self.mensaje.get()
        no_admitidos = [(i, c) for i, c in enumerate(mensaje, 1) if not 32 <= ord(c) <= 126]
        if not mensaje:
            self.pista_mensaje.configure(text="")
        elif no_admitidos:
            posicion, caracter = no_admitidos[0]
            self.pista_mensaje.configure(
                text=f"Carácter no admitido «{caracter}» en la posición {posicion}",
                text_color=AVISO)
        elif len(mensaje) % 2:
            self.pista_mensaje.configure(
                text=f"L = {len(mensaje)}  ·  se agregará un espacio de relleno",
                text_color=TEXTO_TENUE)
        else:
            self.pista_mensaje.configure(text=f"L = {len(mensaje)}", text_color=TEXTO_TENUE)

    def _construir_resultados(self):
        self.indicadores = self._crear_indicadores([
            ("n", "n"), ("phi", "φ"), ("L", "L"), ("relleno", "Relleno"),
            ("llave", "Llave pública"),
        ])

        salida = Tarjeta(self.panel_resultados, "Mensaje cifrado C")
        salida.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        cuerpo = salida.cuerpo
        cuerpo.grid_columnconfigure(0, weight=1)
        self.salida_cifrado = ctk.CTkEntry(cuerpo, height=44, state="readonly",
                                           font=fuente(17, "bold", mono=True))
        self.salida_cifrado.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.detalle_cifrado = ctk.CTkLabel(cuerpo, text="", font=fuente(12),
                                            text_color=TEXTO_TENUE, anchor="w")
        self.detalle_cifrado.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.acciones_salida = ctk.CTkFrame(cuerpo, fg_color="transparent")
        self.acciones_salida.grid(row=1, column=1, sticky="e", pady=(8, 0))
        boton_secundario(self.acciones_salida, "Copiar C", self._copiar_cifrado,
                         width=110).pack(side="left", padx=(8, 0))
        usar = boton_primario(self.acciones_salida, "Usar en Desencriptar  →",
                              self._usar_en_desencriptar)
        usar.configure(height=34, font=fuente(13, "bold"))
        usar.pack(side="left", padx=(8, 0))

        detalle, (pestana_ascii, pestana_bloques) = crear_pestanas_detalle(
            self.panel_resultados, "ASCII", "Bloques")
        detalle.grid(row=2, column=0, sticky="nsew")

        self.tabla_ascii = Tabla(pestana_ascii, [
            ("posicion", "#", 60, "center"), ("caracter", "Carácter", 140, "center"),
            ("codigo", "ASCII", 140, "center"), ("nota", "", 220, "w"),
        ])
        self.tabla_bloques = Tabla(pestana_bloques, [
            ("indice", "#", 60, "center"), ("pareja", "Pareja", 110, "center"),
            ("codigos", "Códigos", 140, "center"), ("m", "m", 140, "center"),
            ("c", "c", 140, "center"),
        ])
        self.tablas = (self.tabla_ascii, self.tabla_bloques)
        for tabla in self.tablas:
            tabla.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

    def _calcular(self):
        return encriptar(self.mensaje.get(), *self.parametros.valores())

    def _mostrar_resultado(self, resultado):
        params = resultado.params
        self.indicadores["n"].mostrar(str(params.n))
        self.indicadores["phi"].mostrar(str(params.phi))
        self.indicadores["L"].mostrar(str(resultado.L))
        if resultado.tiene_relleno:
            self.indicadores["relleno"].mostrar("Sí", AVISO)
        else:
            self.indicadores["relleno"].mostrar("No")
        self.indicadores["llave"].mostrar(f"({params.e}, {params.n})")

        escribir_solo_lectura(self.salida_cifrado, resultado.cifrado)
        detalle = f"L = {resultado.L}"
        if resultado.tiene_relleno:
            detalle += f"   ·   con relleno: «{resultado.mensaje_con_relleno}»"
        self.detalle_cifrado.configure(text=detalle)
        self.acciones_salida.grid()

        self.tabla_ascii.cargar([
            ((c.posicion, caracter_visible(c.caracter), f"{c.codigo:03d}",
              nota_de_caracter(c, "relleno agregado")),
             "relleno" if c.es_relleno else None)
            for c in resultado.caracteres
        ])
        self.tabla_bloques.cargar([
            ((b.indice, f"«{b.pareja}»", f"{ord(b.pareja[0]):03d}  {ord(b.pareja[1]):03d}",
              b.m_str, b.c_str), None)
            for b in resultado.bloques
        ])
        self.barra.mostrar(f"C = {resultado.cifrado}   ·   L = {resultado.L}", "exito")

    def _limpiar_salida(self):
        escribir_solo_lectura(self.salida_cifrado, "")
        self.detalle_cifrado.configure(text="")
        self.acciones_salida.grid_remove()

    def _limpiar_formulario(self):
        self.mensaje.set("")
        self.parametros.limpiar()
        self.entrada_mensaje.focus_set()

    def cargar_ejemplo(self):
        self.mensaje.set(EJEMPLO_MENSAJE)
        self.parametros.establecer(*EJEMPLO_PARAMETROS)

    def _copiar_cifrado(self):
        if self.resultado:
            self._copiar(self.resultado.cifrado, "C")

    def _usar_en_desencriptar(self):
        if self.resultado:
            params = self.resultado.params
            self.al_usar_en_desencriptar(self.resultado.cifrado, self.resultado.L,
                                         params.p, params.q, params.e)


class VistaDesencriptar(_VistaOperacion):
    def __init__(self, master, barra):
        super().__init__(master, barra)
        self._construir_formulario()
        self._construir_resultados()
        self.limpiar_resultados()

    def _construir_formulario(self):
        cuerpo = self.formulario.cuerpo
        self._titulo_campo("Cifrado C")
        self.cifrado = tk.StringVar()
        self.cifrado.trace_add("write", lambda *_: self._describir_cifrado())
        self.entrada_cifrado = ctk.CTkEntry(cuerpo, textvariable=self.cifrado, height=38,
                                            font=fuente(14, mono=True))
        self.entrada_cifrado.pack(fill="x", pady=(4, 2))
        self.pista_cifrado = self._pista()
        self.pista_cifrado.pack(fill="x")

        self._titulo_campo("Longitud L", pady=(10, 0))
        self.longitud = tk.StringVar()
        self.entrada_longitud = ctk.CTkEntry(cuerpo, textvariable=self.longitud, height=38,
                                             width=120, font=fuente(14, mono=True))
        self.entrada_longitud.pack(anchor="w", pady=(4, 2))

        self._separador()
        self.parametros = FormularioParametros(cuerpo)
        self.parametros.pack(fill="x")
        self._acciones("Desencriptar")
        self._ejecutar_con_enter(self.entrada_cifrado, self.entrada_longitud,
                                 *self.parametros.entradas)

    def _describir_cifrado(self):
        cantidad = len(self.cifrado.get().split())
        if cantidad == 0:
            self.pista_cifrado.configure(text="")
        else:
            self.pista_cifrado.configure(
                text=f"{cantidad} bloque(s)  ·  L = {2 * cantidad} o {2 * cantidad - 1}",
                text_color=TEXTO_TENUE)

    def _construir_resultados(self):
        self.indicadores = self._crear_indicadores([
            ("n", "n"), ("phi", "φ"), ("d", "d"), ("L", "L"), ("relleno", "Relleno"),
            ("llave", "Llave privada"),
        ])

        salida = Tarjeta(self.panel_resultados, "Mensaje recuperado M")
        salida.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        cuerpo = salida.cuerpo
        cuerpo.grid_columnconfigure(0, weight=1)
        self.salida_mensaje = ctk.CTkEntry(cuerpo, height=44, state="readonly",
                                           font=fuente(17, "bold", mono=True))
        self.salida_mensaje.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.detalle_mensaje = ctk.CTkLabel(cuerpo, text="", font=fuente(12),
                                            text_color=EXITO, anchor="w")
        self.detalle_mensaje.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.acciones_salida = ctk.CTkFrame(cuerpo, fg_color="transparent")
        self.acciones_salida.grid(row=1, column=1, sticky="e", pady=(8, 0))
        self.ver_espacios = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.acciones_salida, text="Ver espacios", variable=self.ver_espacios,
                        command=self._pintar_mensaje, font=fuente(12), text_color=TEXTO,
                        fg_color=VERDE_UVG, hover_color=VERDE_UVG_OSCURO,
                        checkbox_width=18, checkbox_height=18).pack(side="left", padx=(8, 0))
        boton_secundario(self.acciones_salida, "Copiar M", self._copiar_mensaje,
                         width=110).pack(side="left", padx=(8, 0))

        detalle, (pestana_bloques, pestana_ascii) = crear_pestanas_detalle(
            self.panel_resultados, "Bloques", "ASCII")
        detalle.grid(row=2, column=0, sticky="nsew")

        self.tabla_bloques = Tabla(pestana_bloques, [
            ("indice", "#", 60, "center"), ("c", "c", 140, "center"),
            ("m", "m", 140, "center"), ("codigos", "Códigos", 140, "center"),
            ("pareja", "Pareja", 110, "center"),
        ])
        self.tabla_ascii = Tabla(pestana_ascii, [
            ("posicion", "#", 60, "center"), ("codigo", "ASCII", 140, "center"),
            ("caracter", "Carácter", 140, "center"), ("nota", "", 220, "w"),
        ])
        self.tablas = (self.tabla_bloques, self.tabla_ascii)
        for tabla in self.tablas:
            tabla.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

    def _calcular(self):
        return desencriptar(self.cifrado.get(), self.longitud.get(), *self.parametros.valores())

    def _mostrar_resultado(self, resultado):
        params = resultado.params
        self.indicadores["n"].mostrar(str(params.n))
        self.indicadores["phi"].mostrar(str(params.phi))
        self.indicadores["d"].mostrar(str(resultado.d))
        self.indicadores["L"].mostrar(str(resultado.L))
        if resultado.tiene_relleno:
            self.indicadores["relleno"].mostrar("Sí", AVISO)
        else:
            self.indicadores["relleno"].mostrar("No")
        self.indicadores["llave"].mostrar(f"({resultado.d}, {params.n})")

        self._pintar_mensaje()
        detalle = f"✓  {len(resultado.mensaje)} caracteres, coincide con L"
        if resultado.tiene_relleno:
            detalle += "   ·   relleno retirado"
        self.detalle_mensaje.configure(text=detalle)
        self.acciones_salida.grid()

        self.tabla_bloques.cargar([
            ((b.indice, b.c_str, b.m_str, f"{b.m_str[:3]}  {b.m_str[3:]}", f"«{b.pareja}»"),
             None)
            for b in resultado.bloques
        ])
        self.tabla_ascii.cargar([
            ((c.posicion, f"{c.codigo:03d}", caracter_visible(c.caracter),
              nota_de_caracter(c, "relleno retirado")),
             "relleno" if c.es_relleno else None)
            for c in resultado.caracteres
        ])
        self.barra.mostrar(f"M = «{resultado.mensaje}»   ·   d = {resultado.d}", "exito")

    def _pintar_mensaje(self):
        if self.resultado:
            mensaje = self.resultado.mensaje
            if self.ver_espacios.get():
                mensaje = mensaje.replace(" ", "␣")
            escribir_solo_lectura(self.salida_mensaje, mensaje)

    def _limpiar_salida(self):
        escribir_solo_lectura(self.salida_mensaje, "")
        self.detalle_mensaje.configure(text="")
        self.acciones_salida.grid_remove()

    def _limpiar_formulario(self):
        self.cifrado.set("")
        self.longitud.set("")
        self.parametros.limpiar()
        self.entrada_cifrado.focus_set()

    def cargar_ejemplo(self):
        self.recibir(EJEMPLO_CIFRADO, EJEMPLO_L, *EJEMPLO_PARAMETROS)

    def recibir(self, cifrado, longitud, p, q, e):
        self.cifrado.set(cifrado)
        self.longitud.set(str(longitud))
        self.parametros.establecer(p, q, e)
        self.mensaje_error.configure(text="")
        self.limpiar_resultados()

    def _copiar_mensaje(self):
        if self.resultado:
            self._copiar(self.resultado.mensaje, "M")


class VistaComprobaciones(ctk.CTkFrame):
    def __init__(self, master, barra):
        super().__init__(master, fg_color="transparent")
        self.barra = barra
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = Tarjeta(self, "Comprobaciones")
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        cuerpo = encabezado.cuerpo
        cuerpo.grid_columnconfigure(1, weight=1)
        boton_primario(cuerpo, "Ejecutar", self.ejecutar, width=160).grid(row=0, column=0)
        self.resumen = ctk.CTkLabel(cuerpo, text="", font=fuente(15, "bold"), anchor="w")
        self.resumen.grid(row=0, column=1, sticky="w", padx=16)

        marco = Tarjeta(self)
        marco.grid(row=1, column=0, sticky="nsew")
        marco.cuerpo.grid_columnconfigure(0, weight=1)
        marco.cuerpo.grid_rowconfigure(0, weight=1)
        self.tabla = Tabla(marco.cuerpo, [
            ("resultado", "", 70, "center"), ("nombre", "Caso", 280, "w"),
            ("detalle", "Detalle", 700, "w"),
        ])
        self.tabla.grid(row=0, column=0, sticky="nsew")

    def ejecutar(self):
        resultados = ejecutar_todas()
        superadas = sum(r.superada for r in resultados)
        total = len(resultados)
        self.tabla.cargar([
            (("✓" if r.superada else "✕", r.nombre, r.detalle),
             "exito" if r.superada else "error")
            for r in resultados
        ])
        todas = superadas == total
        self.resumen.configure(text=f"{superadas} de {total} superadas",
                               text_color=EXITO if todas else ERROR)
        self.barra.mostrar(f"{superadas} de {total} comprobaciones superadas",
                           "exito" if todas else "error")
