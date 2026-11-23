"""Algoritmos de teoría de números implementados sin funciones de la biblioteca estándar.

No se utiliza ``math.gcd`` ni ``pow`` con módulo: la primalidad, el máximo común
divisor, el inverso modular y la exponenciación modular se calculan aquí.
"""


def es_primo(n: int) -> bool:
    """Indica si ``n`` es primo mediante división de prueba hasta su raíz cuadrada."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    divisor = 5
    while divisor * divisor <= n:
        if n % divisor == 0 or n % (divisor + 2) == 0:
            return False
        divisor += 6
    return True


def mcd(a: int, b: int) -> int:
    """Máximo común divisor de ``a`` y ``b`` con el algoritmo de Euclides."""
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a


def euclides_extendido(a: int, b: int) -> tuple[int, int, int]:
    """Devuelve ``(g, x, y)`` tales que ``a*x + b*y = g = MCD(a, b)``."""
    resto_anterior, resto = a, b
    x_anterior, x = 1, 0
    y_anterior, y = 0, 1
    while resto != 0:
        cociente = resto_anterior // resto
        resto_anterior, resto = resto, resto_anterior - cociente * resto
        x_anterior, x = x, x_anterior - cociente * x
        y_anterior, y = y, y_anterior - cociente * y
    return resto_anterior, x_anterior, y_anterior


def inverso_modular(a: int, m: int) -> int:
    """Inverso de ``a`` módulo ``m`` en el rango ``1 <= d < m``.

    Raises:
        ValueError: si ``a`` y ``m`` no son primos relativos.
    """
    g, x, _ = euclides_extendido(a % m, m)
    if g != 1:
        raise ValueError(f"{a} no tiene inverso módulo {m} (MCD = {g}).")
    return x % m


def exp_modular(base: int, exponente: int, modulo: int) -> int:
    """Calcula ``base**exponente mod modulo`` por cuadrado y multiplicación.

    Cada producto se reduce módulo ``modulo`` en el momento, por lo que nunca se
    construye la potencia completa.
    """
    if modulo == 1:
        return 0
    resultado = 1
    base %= modulo
    while exponente > 0:
        if exponente % 2 == 1:
            resultado = (resultado * base) % modulo
        base = (base * base) % modulo
        exponente //= 2
    return resultado
