"""Interfaz web RSA: python -m streamlit run app.py.

Los cálculos usan el mismo rsa_core de la versión de escritorio.
Cada visitante mantiene los datos en su propia sesión de Streamlit.
"""
from pathlib import Path

import streamlit as st

from rsa_core import ErrorValidacion, desencriptar, encriptar
from rsa_core.comprobaciones import ejecutar_todas

RAIZ = Path(__file__).resolve().parent
EJEMPLO = {"p": "367", "q": "373", "e": "17"}


def invalidar(prefijo):
    """Retira resultados y errores cuando cambian las entradas."""
    st.session_state.pop(f"{prefijo}_resultado", None)
    st.session_state.pop(f"{prefijo}_error", None)
    if prefijo == "enc":
        st.session_state.pop("transferido", None)


def cargar_ejemplo(prefijo):
    invalidar(prefijo)
    for nombre, valor in EJEMPLO.items():
        st.session_state[f"{prefijo}_{nombre}"] = valor
    if prefijo == "enc":
        st.session_state.enc_mensaje = "RSA"
    else:
        st.session_state.dec_cifrado = "026054 123875"
        st.session_state.dec_longitud = "3"


def transferir():
    resultado = st.session_state.get("enc_resultado")
    if resultado is None:
        return
    invalidar("dec")
    st.session_state.dec_cifrado = resultado.cifrado
    st.session_state.dec_longitud = str(resultado.L)
    for nombre in EJEMPLO:
        st.session_state[f"dec_{nombre}"] = str(getattr(resultado.params, nombre))
    st.session_state.transferido = True


def inicializar():
    for prefijo in ("enc", "dec"):
        for nombre, valor in EJEMPLO.items():
            st.session_state.setdefault(f"{prefijo}_{nombre}", valor)
    for nombre in ("enc_mensaje", "dec_cifrado", "dec_longitud"):
        st.session_state.setdefault(nombre, "")


def parametros(prefijo):
    ayudas = {"p": "Primo distinto de q.", "q": "Primo distinto de p.",
              "e": "Entero mayor que 1 y primo relativo con φ(n)."}
    for columna, nombre in zip(st.columns(3), EJEMPLO):
        columna.text_input(nombre, key=f"{prefijo}_{nombre}", help=ayudas[nombre],
                           on_change=invalidar, args=(prefijo,))


def valores_parametros(prefijo):
    return [st.session_state[f"{prefijo}_{nombre}"] for nombre in EJEMPLO]


def calcular(prefijo):
    invalidar(prefijo)
    try:
        if prefijo == "enc":
            resultado = encriptar(st.session_state.enc_mensaje, *valores_parametros(prefijo))
        else:
            resultado = desencriptar(st.session_state.dec_cifrado,
                                     st.session_state.dec_longitud, *valores_parametros(prefijo))
    except ErrorValidacion as error:
        st.session_state[f"{prefijo}_error"] = str(error)
    else:
        st.session_state[f"{prefijo}_resultado"] = resultado


def indicadores(resultado, descifrado=False):
    for columna, titulo, valor in zip(
        st.columns(4), ("n", "φ(n)", "Longitud original L", "Relleno"),
        (resultado.params.n, resultado.params.phi, resultado.L,
         "Sí" if resultado.tiene_relleno else "No"),
    ):
        columna.metric(titulo, valor)
    if descifrado:
        st.markdown(f"**Exponente privado d:** `{resultado.d}`")
        st.markdown(f"**Llave privada (d, n):** `({resultado.d}, {resultado.params.n})`")
    else:
        st.markdown(f"**Llave pública (e, n):** `({resultado.params.e}, {resultado.params.n})`")


def detalle(resultado, descifrado=False):
    st.subheader("Detalle del proceso")
    st.caption("␣ representa un espacio. Los ceros iniciales forman parte del formato.")
    ascii_tab, bloques_tab = st.tabs(["ASCII", "Bloques"])
    with ascii_tab:
        st.dataframe(
            [{"Posición": c.posicion, "Carácter": "␣" if c.caracter == " " else c.caracter,
              "ASCII": f"{c.codigo:03d}",
              "Detalle": ("Relleno retirado" if descifrado else "Relleno agregado")
              if c.es_relleno else "Original"} for c in resultado.caracteres],
            hide_index=True, width="stretch",
        )
    with bloques_tab:
        filas = []
        for b in resultado.bloques:
            fila = {"Bloque": b.indice}
            if descifrado:
                fila.update({"c (antes)": b.c_str, "m (después)": b.m_str})
            else:
                fila.update({"m (antes)": b.m_str, "c (después)": b.c_str})
            fila.update({"Códigos ASCII": f"{b.m_str[:3]} {b.m_str[3:]}",
                         "Pareja": b.pareja.replace(" ", "␣")})
            filas.append(fila)
        st.dataframe(filas, hide_index=True, width="stretch")
        st.latex(r"m = c^d \bmod n" if descifrado else r"c = m^e \bmod n")


def vista_encriptar():
    entrada, salida = st.columns([1, 1.35], gap="large")
    with entrada:
        st.subheader("Tu mensaje")
        st.caption("ASCII imprimible: letras sin tilde, números, signos y espacios.")
        st.button("Cargar ejemplo", key="ejemplo_enc", on_click=cargar_ejemplo, args=("enc",))
        st.text_area("Mensaje M", key="enc_mensaje", height=120,
                     placeholder="Escribe tu mensaje aquí…", on_change=invalidar, args=("enc",),
                     help="Se conservan los espacios. No se admiten ñ, tildes, tabulaciones ni saltos de línea.")
        parametros("enc")
        st.caption("p ≠ q · 126126 < n < 1000000 · e > 1 · MCD(e, φ) = 1")
        st.button("Encriptar", key="calcular_enc", type="primary", width="stretch",
                  on_click=calcular, args=("enc",))
        if st.session_state.get("enc_error"):
            st.error(st.session_state.enc_error)
    with salida:
        resultado = st.session_state.get("enc_resultado")
        if resultado is None:
            st.info("Ingresa un mensaje o carga el ejemplo y pulsa Encriptar.")
            return
        indicadores(resultado)
        st.subheader("Mensaje cifrado C")
        st.code(resultado.cifrado, language=None)
        st.caption("Copia C con el botón de la esquina del bloque. Conserva también L.")
        if resultado.tiene_relleno:
            st.info("Se agregó exactamente un espacio (ASCII 032) para completar la última pareja.")
        else:
            st.success("La longitud es par: no se agregó relleno.")
        st.caption("Mensaje procesado, con los espacios visibles:")
        st.code(resultado.mensaje_con_relleno.replace(" ", "␣"), language=None)
        st.button("Usar en Desencriptar →", key="transferir", on_click=transferir)
        if st.session_state.get("transferido"):
            st.success("C, L y los parámetros están listos. Abre la pestaña Desencriptar y pulsa Desencriptar.")
        st.download_button(
            "Descargar C y L", data=(f"C: {resultado.cifrado}\nL: {resultado.L}\n"
                                     f"Llave pública: ({resultado.params.e}, {resultado.params.n})\n"),
            file_name="cifrado_RSA.txt", mime="text/plain; charset=utf-8", on_click="ignore",
        )
        detalle(resultado)


def vista_desencriptar():
    entrada, salida = st.columns([1, 1.35], gap="large")
    with entrada:
        st.subheader("Recupera el mensaje")
        st.caption("Ingresa C, L y los mismos p, q y e usados al encriptar.")
        st.button("Cargar ejemplo", key="ejemplo_dec", on_click=cargar_ejemplo, args=("dec",))
        st.text_area("Cifrado C", key="dec_cifrado", height=100,
                     placeholder="026054 123875", on_change=invalidar, args=("dec",),
                     help="Bloques de exactamente seis dígitos, separados por un espacio.")
        st.text_input("Longitud original L", key="dec_longitud", on_change=invalidar, args=("dec",))
        st.caption("Para k bloques, L debe ser 2k o 2k − 1.")
        parametros("dec")
        st.button("Desencriptar", key="calcular_dec", type="primary", width="stretch",
                  on_click=calcular, args=("dec",))
        if st.session_state.get("dec_error"):
            st.error(st.session_state.dec_error)
    with salida:
        resultado = st.session_state.get("dec_resultado")
        if resultado is None:
            st.info("Carga el ejemplo, transfiere un cifrado o ingresa los datos para desencriptar.")
            return
        indicadores(resultado, descifrado=True)
        st.subheader("Mensaje recuperado M")
        ver_espacios = st.checkbox("Ver espacios", key="ver_espacios")
        mensaje = resultado.mensaje.replace(" ", "␣") if ver_espacios else resultado.mensaje
        st.code(mensaje, language=None)
        st.success(f"Mensaje recuperado: {len(resultado.mensaje)} caracteres, coincide con L.")
        st.caption("Coincidir con L verifica la longitud. Para comprobar el contenido, compáralo con el original.")
        if resultado.tiene_relleno:
            st.info("Se verificó y retiró exactamente el último espacio de relleno. Los espacios originales se conservan.")
        else:
            st.caption("No se retiró ningún carácter: L es par.")
        st.download_button("Descargar mensaje original", data=resultado.mensaje.encode("ascii"),
                           file_name="mensaje_RSA.txt", mime="text/plain", on_click="ignore")
        detalle(resultado, descifrado=True)


def vista_comprobaciones():
    st.subheader("Comprueba el funcionamiento")
    st.write("Ejecuta los 20 casos del proyecto: recuperación exacta y rechazo de datos inválidos.")
    if st.button("Ejecutar comprobaciones", key="comprobar", type="primary"):
        st.session_state.comprobaciones = ejecutar_todas()
    resultados = st.session_state.get("comprobaciones")
    if resultados is not None:
        total = len(resultados)
        superadas = sum(r.superada for r in resultados)
        texto = f"{superadas} de {total} superadas"
        if superadas == total:
            st.success(texto)
        else:
            st.error(texto)
        st.dataframe(
            [{"Resultado": "Correcto" if r.superada else "Fallo", "Caso": r.nombre,
              "Detalle": r.detalle} for r in resultados],
            hide_index=True, width="stretch", height=600,
        )


def main():
    st.set_page_config(page_title="Criptografía RSA · Grupo 1", page_icon="🔐", layout="wide")
    inicializar()
    st.markdown("""<style>
        .block-container {max-width: 1350px; padding-top: 2.2rem; padding-bottom: 3rem;}
        h1 {letter-spacing: -.04em;}
        [data-testid="stMetric"] {background: #edf4ef; border-radius: 12px; padding: 12px;}
        [data-testid="stMetricValue"] {font-size: 1.55rem; color: #174b35;}
        [data-testid="stTabs"] button {font-size: 1rem;}
        </style>""", unsafe_allow_html=True)
    logo, encabezado = st.columns([1, 9], vertical_alignment="center")
    with logo:
        ruta_logo = RAIZ / "assets" / "logo_uvg.png"
        if ruta_logo.is_file():
            st.image(str(ruta_logo), width=80)
    with encabezado:
        st.caption("MM2015 · MATEMÁTICA DISCRETA 1 · GRUPO 1")
        st.title("Criptografía RSA")
        st.write("Del texto a los números. Encripta, recupera y explora cada paso.")
    st.caption("Sebastian Rodas · Fabricio Estrada")
    st.divider()
    enc, dec, pruebas = st.tabs(["Encriptar", "Desencriptar", "Comprobaciones"])
    with enc:
        vista_encriptar()
    with dec:
        vista_desencriptar()
    with pruebas:
        vista_comprobaciones()
    st.divider()
    with st.expander("Fundamento matemático y uso"):
        st.latex(r"n=pq,\qquad \varphi(n)=(p-1)(q-1),\qquad ed\equiv1\pmod{\varphi(n)}")
        st.latex(r"c=m^e\bmod n,\qquad m=c^d\bmod n")
        st.write("Cada bloque contiene dos caracteres ASCII de tres dígitos cada uno. "
                 "Si la longitud original L es impar, se agrega un espacio de relleno. "
                 "Al desencriptar, L permite retirar solo ese espacio y conservar los originales. "
                 "El símbolo ␣ solo se usa para visualizar espacios.")
        st.write("Primalidad por división de prueba; MCD por Euclides; inverso modular por "
                 "Euclides extendido; potencias por cuadrados y multiplicación con reducción modular.")
        st.caption("Los datos se mantienen en la sesión del navegador; al recargarla se reinician.")


if __name__ == "__main__":
    main()
