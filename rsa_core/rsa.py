"""Encriptación y desencriptación RSA por bloques de dos caracteres ASCII.

Las funciones públicas reciben los datos como texto, tal como se escriben en la
interfaz, y devuelven un objeto con el detalle de cada paso. Cualquier dato
inválido produce un ``ErrorValidacion`` con un mensaje apto para el usuario.
"""

import re
from dataclasses import dataclass, field

from .matematica import es_primo, exp_modular, inverso_modular, mcd

ASCII_MIN, ASCII_MAX = 32, 126
N_MIN, N_MAX = 126126, 1_000_000
CARACTER_RELLENO = " "

_PATRON_ENTERO = re.compile(r"^[+-]?\d+$")
_PATRON_BLOQUE = re.compile(r"^[0-9]{6}$")


class ErrorValidacion(Exception):
    """Dato de entrada inválido; su mensaje se muestra tal cual al usuario."""


@dataclass
class ParametrosRSA:
    p: int
    q: int
    e: int
    n: int
    phi: int


@dataclass
class Caracter:
    posicion: int
    caracter: str
    codigo: int
    es_relleno: bool = False


@dataclass
class Bloque:
    indice: int
    pareja: str
    m: int
    c: int

    @property
    def m_str(self) -> str:
        return f"{self.m:06d}"

    @property
    def c_str(self) -> str:
        return f"{self.c:06d}"


@dataclass
class ResultadoEncriptacion:
    params: ParametrosRSA
    mensaje: str
    L: int
    tiene_relleno: bool
    mensaje_con_relleno: str
    caracteres: list[Caracter] = field(default_factory=list)
    bloques: list[Bloque] = field(default_factory=list)

    @property
    def cifrado(self) -> str:
        return " ".join(b.c_str for b in self.bloques)


@dataclass
class ResultadoDesencriptacion:
    params: ParametrosRSA
    d: int
    L: int
    tiene_relleno: bool
    mensaje: str
    mensaje_con_relleno: str
    caracteres: list[Caracter] = field(default_factory=list)
    bloques: list[Bloque] = field(default_factory=list)


def _leer_entero(texto: str, nombre: str) -> int:
    texto = (texto or "").strip()
    if texto == "":
        raise ErrorValidacion(f"Falta ingresar {nombre}.")
    if not _PATRON_ENTERO.match(texto):
        raise ErrorValidacion(f"{nombre} debe ser un número entero (se recibió «{texto}»).")
    return int(texto)


def validar_parametros(p_txt: str, q_txt: str, e_txt: str) -> ParametrosRSA:
    """Valida p, q y e según el enunciado y calcula n y φ."""
    p = _leer_entero(p_txt, "p")
    q = _leer_entero(q_txt, "q")
    e = _leer_entero(e_txt, "e")

    if not es_primo(p):
        raise ErrorValidacion(f"p = {p} no es un número primo.")
    if not es_primo(q):
        raise ErrorValidacion(f"q = {q} no es un número primo.")
    if p == q:
        raise ErrorValidacion("p y q deben ser primos distintos.")

    n = p * q
    if not N_MIN < n < N_MAX:
        raise ErrorValidacion(f"n = {n} está fuera de rango; debe cumplir {N_MIN} < n < {N_MAX}.")
    phi = (p - 1) * (q - 1)

    if e <= 1:
        raise ErrorValidacion(f"e = {e} no es válido; debe ser mayor que 1.")
    divisor_comun = mcd(e, phi)
    if divisor_comun != 1:
        raise ErrorValidacion(
            f"e = {e} no es primo relativo con φ = {phi} (MCD = {divisor_comun})."
        )
    return ParametrosRSA(p, q, e, n, phi)


def _describir(caracter: str) -> str:
    if caracter == "\t":
        return "una tabulación"
    if caracter in "\r\n":
        return "un salto de línea"
    return f"«{caracter}»"


def validar_mensaje(mensaje: str) -> None:
    """Verifica que el mensaje no esté vacío y solo tenga ASCII imprimible."""
    if mensaje == "":
        raise ErrorValidacion("El mensaje está vacío.")
    for posicion, caracter in enumerate(mensaje, start=1):
        if not ASCII_MIN <= ord(caracter) <= ASCII_MAX:
            raise ErrorValidacion(
                f"Carácter no admitido en la posición {posicion}: {_describir(caracter)}. "
                f"Solo se aceptan caracteres ASCII imprimibles (sin tildes ni ñ)."
            )


def _detallar_caracteres(texto: str, tiene_relleno: bool) -> list[Caracter]:
    ultima_posicion = len(texto)
    return [
        Caracter(posicion, caracter, ord(caracter),
                 es_relleno=tiene_relleno and posicion == ultima_posicion)
        for posicion, caracter in enumerate(texto, start=1)
    ]


def encriptar(mensaje: str, p_txt: str, q_txt: str, e_txt: str) -> ResultadoEncriptacion:
    """Encripta ``mensaje`` con la llave pública derivada de p, q y e."""
    validar_mensaje(mensaje)
    params = validar_parametros(p_txt, q_txt, e_txt)

    L = len(mensaje)
    tiene_relleno = L % 2 == 1
    texto = mensaje + CARACTER_RELLENO if tiene_relleno else mensaje

    bloques = []
    for inicio in range(0, len(texto), 2):
        pareja = texto[inicio:inicio + 2]
        m = int(f"{ord(pareja[0]):03d}{ord(pareja[1]):03d}")
        c = exp_modular(m, params.e, params.n)
        bloques.append(Bloque(len(bloques) + 1, pareja, m, c))

    return ResultadoEncriptacion(params, mensaje, L, tiene_relleno, texto,
                                 _detallar_caracteres(texto, tiene_relleno), bloques)


def _leer_bloques_cifrados(cifrado_txt: str, n: int) -> list[int]:
    cifrado_txt = (cifrado_txt or "").strip()
    if cifrado_txt == "":
        raise ErrorValidacion("El cifrado C está vacío.")
    fragmentos = cifrado_txt.split(" ")
    if "" in fragmentos:
        raise ErrorValidacion("Los bloques de C deben estar separados por un solo espacio.")

    valores = []
    for indice, fragmento in enumerate(fragmentos, start=1):
        if not _PATRON_BLOQUE.match(fragmento):
            raise ErrorValidacion(
                f"Bloque {indice} de C mal formado («{fragmento}»): "
                f"debe tener exactamente 6 dígitos."
            )
        c = int(fragmento)
        if c >= n:
            raise ErrorValidacion(f"Bloque {indice} de C fuera de rango: {fragmento} ≥ n = {n}.")
        valores.append(c)
    return valores


def _leer_longitud(L_txt: str, cantidad_bloques: int) -> int:
    L = _leer_entero(L_txt, "la longitud L")
    sin_relleno, con_relleno = 2 * cantidad_bloques, 2 * cantidad_bloques - 1
    if L not in (sin_relleno, con_relleno):
        raise ErrorValidacion(
            f"L = {L} no es coherente con C: con {cantidad_bloques} bloque(s), "
            f"L debe ser {sin_relleno} o {con_relleno}."
        )
    return L


def _bloque_a_pareja(indice: int, m: int) -> str:
    m_str = f"{m:06d}"
    codigos = (int(m_str[:3]), int(m_str[3:]))
    for codigo in codigos:
        if not ASCII_MIN <= codigo <= ASCII_MAX:
            raise ErrorValidacion(
                f"El bloque {indice} se descifró como {m_str}, con el código {codigo:03d} "
                f"fuera del rango 032–126. Revise C, p, q y e."
            )
    return chr(codigos[0]) + chr(codigos[1])


def desencriptar(cifrado_txt: str, L_txt: str, p_txt: str, q_txt: str,
                 e_txt: str) -> ResultadoDesencriptacion:
    """Recupera el mensaje original a partir de C, L, p, q y e."""
    params = validar_parametros(p_txt, q_txt, e_txt)
    valores = _leer_bloques_cifrados(cifrado_txt, params.n)
    L = _leer_longitud(L_txt, len(valores))
    tiene_relleno = L % 2 == 1
    d = inverso_modular(params.e, params.phi)

    bloques = []
    for indice, c in enumerate(valores, start=1):
        m = exp_modular(c, d, params.n)
        bloques.append(Bloque(indice, _bloque_a_pareja(indice, m), m, c))
    texto = "".join(b.pareja for b in bloques)

    if tiene_relleno:
        if texto[-1] != CARACTER_RELLENO:
            raise ErrorValidacion(
                f"L = {L} es impar, pero el último carácter recuperado es «{texto[-1]}» "
                f"y no un espacio de relleno."
            )
        mensaje = texto[:-1]
    else:
        mensaje = texto

    return ResultadoDesencriptacion(params, d, L, tiene_relleno, mensaje, texto,
                                    _detallar_caracteres(texto, tiene_relleno), bloques)
