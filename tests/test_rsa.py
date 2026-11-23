"""Pruebas automáticas de la lógica RSA.

Ejecutar desde la raíz del proyecto: ``python -m unittest discover -s tests``.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from rsa_core import (ErrorValidacion, desencriptar, encriptar, es_primo, exp_modular,
                      inverso_modular, mcd)
from rsa_core.comprobaciones import ejecutar_todas


class TestAlgoritmos(unittest.TestCase):
    def test_mcd(self):
        self.assertEqual(mcd(17, 136152), 1)
        self.assertEqual(mcd(48, 18), 6)
        self.assertEqual(mcd(0, 5), 5)

    def test_es_primo(self):
        self.assertTrue(all(es_primo(x) for x in (2, 3, 5, 367, 373, 997)))
        self.assertFalse(any(es_primo(x) for x in (0, 1, 4, 368, 1001)))

    def test_inverso_modular(self):
        self.assertEqual(inverso_modular(17, 136152), 8009)
        with self.assertRaises(ValueError):
            inverso_modular(2, 136152)

    def test_exp_modular_coincide_con_la_definicion(self):
        for base in range(30):
            for exponente in range(15):
                self.assertEqual(exp_modular(base, exponente, 97), (base ** exponente) % 97)


class TestRSA(unittest.TestCase):
    def test_comprobaciones_del_enunciado(self):
        for comprobacion in ejecutar_todas():
            with self.subTest(comprobacion.nombre):
                self.assertTrue(comprobacion.superada, comprobacion.detalle)

    def test_todos_los_caracteres_admitidos(self):
        mensaje = "".join(chr(codigo) for codigo in range(32, 127))
        cifrado = encriptar(mensaje, "367", "373", "17")
        recuperado = desencriptar(cifrado.cifrado, str(cifrado.L), "367", "373", "17")
        self.assertEqual(recuperado.mensaje, mensaje)

    def test_mensaje_vacio(self):
        with self.assertRaises(ErrorValidacion):
            encriptar("", "367", "373", "17")


if __name__ == "__main__":
    unittest.main()
