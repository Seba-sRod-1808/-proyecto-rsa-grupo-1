"""Casos de prueba exigidos por el enunciado.

Los utilizan la pestaña «Comprobaciones» de la interfaz y ``tests/test_rsa.py``.
Todos usan los parámetros del ejemplo de referencia: p = 367, q = 373, e = 17.
"""

from dataclasses import dataclass

from .rsa import ErrorValidacion, desencriptar, encriptar

P, Q, E = "367", "373", "17"


@dataclass
class ResultadoComprobacion:
    nombre: str
    detalle: str
    superada: bool


def _recupera_exacto(nombre: str, mensaje: str) -> ResultadoComprobacion:
    try:
        cifrado = encriptar(mensaje, P, Q, E)
        recuperado = desencriptar(cifrado.cifrado, str(cifrado.L), P, Q, E)
    except ErrorValidacion as error:
        return ResultadoComprobacion(nombre, f"Error inesperado: {error}", False)
    return ResultadoComprobacion(nombre, f"«{mensaje}» → {cifrado.cifrado}",
                                 recuperado.mensaje == mensaje)


def _es_rechazado(nombre: str, operacion, *datos) -> ResultadoComprobacion:
    try:
        operacion(*datos)
    except ErrorValidacion as error:
        return ResultadoComprobacion(nombre, str(error), True)
    return ResultadoComprobacion(nombre, "Se aceptó un dato inválido.", False)


def _ejemplo_de_referencia() -> ResultadoComprobacion:
    cifrado = encriptar("RSA", P, Q, E)
    recuperado = desencriptar(cifrado.cifrado, str(cifrado.L), P, Q, E)
    coincide = (
        cifrado.params.n == 136891
        and cifrado.params.phi == 136152
        and cifrado.L == 3
        and cifrado.mensaje_con_relleno == "RSA "
        and " ".join(b.m_str for b in cifrado.bloques) == "082083 065032"
        and cifrado.cifrado == "026054 123875"
        and recuperado.d == 8009
        and recuperado.mensaje == "RSA"
    )
    return ResultadoComprobacion(
        "Ejemplo de referencia",
        f"C = {cifrado.cifrado}, d = {recuperado.d}, M = «{recuperado.mensaje}»",
        coincide,
    )


def ejecutar_todas() -> list[ResultadoComprobacion]:
    cifrado_par = encriptar("Hola", P, Q, E).cifrado
    return [
        _ejemplo_de_referencia(),
        _recupera_exacto("Longitud par", "Hola"),
        _recupera_exacto("Longitud impar", "Hola!"),
        _recupera_exacto("Un solo carácter", "A"),
        _recupera_exacto("Mayúsculas y minúsculas", "MaTeMaTiCa DiScReTa"),
        _recupera_exacto("Números y signos", "2+2=4? {ok} [#1] ~@$%^&*"),
        _recupera_exacto("Espacios consecutivos", "a  b   c"),
        _recupera_exacto("Espacios al inicio y al final", "   hola mundo   "),
        _recupera_exacto("Ceros iniciales en el cifrado", "RSA"),
        _es_rechazado("p no primo", encriptar, "Hola", "368", Q, E),
        _es_rechazado("p y q iguales", encriptar, "Hola", "367", "367", E),
        _es_rechazado("n fuera de rango", encriptar, "Hola", "11", "13", E),
        _es_rechazado("e no coprimo con φ", encriptar, "Hola", P, Q, "2"),
        _es_rechazado("e no entero", encriptar, "Hola", P, Q, "abc"),
        _es_rechazado("Carácter no admitido", encriptar, "año", P, Q, E),
        _es_rechazado("Bloque con 5 dígitos", desencriptar, "02605 123875", "3", P, Q, E),
        _es_rechazado("Bloque con letras", desencriptar, "02605A 123875", "3", P, Q, E),
        _es_rechazado("Bloque fuera de rango", desencriptar, "999999", "2", P, Q, E),
        _es_rechazado("Longitud inconsistente", desencriptar, "026054 123875", "5", P, Q, E),
        _es_rechazado("L impar sin relleno", desencriptar, cifrado_par, "3", P, Q, E),
    ]
