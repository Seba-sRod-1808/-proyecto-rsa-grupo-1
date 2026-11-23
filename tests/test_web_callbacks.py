"""Pruebas del enlace entre los controles web y RSA, sin necesitar un servidor."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


class Estado(dict):
    """Estado mínimo para probar los callbacks sin importar Streamlit."""
    def __getattr__(self, nombre):
        try:
            return self[nombre]
        except KeyError as error:
            raise AttributeError(nombre) from error

    def __setattr__(self, nombre, valor):
        self[nombre] = valor


class TestCallbacksWeb(unittest.TestCase):
    def setUp(self):
        self.streamlit = ModuleType("streamlit")
        self.streamlit.session_state = Estado()
        spec = importlib.util.spec_from_file_location("app_bajo_prueba", RAIZ / "app.py")
        self.app = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"streamlit": self.streamlit}):
            spec.loader.exec_module(self.app)
        self.estado = self.streamlit.session_state
        self.app.inicializar()

    def test_ejemplo_transferencia_y_recuperacion(self):
        self.app.cargar_ejemplo("enc")
        self.app.calcular("enc")
        self.assertEqual(self.estado.enc_resultado.cifrado, "026054 123875")
        self.app.transferir()
        self.assertEqual(self.estado.dec_longitud, "3")
        self.assertEqual(self.estado.dec_cifrado, "026054 123875")
        self.app.calcular("dec")
        self.assertEqual(self.estado.dec_resultado.mensaje, "RSA")
        self.assertEqual(self.estado.dec_resultado.d, 8009)

    def test_transferencia_con_parametros_distintos(self):
        self.estado.enc_mensaje = "AB"
        self.estado.enc_p = "401"
        self.estado.enc_q = "409"
        self.estado.enc_e = "7"
        self.app.calcular("enc")
        self.app.transferir()
        self.assertEqual((self.estado.dec_p, self.estado.dec_q, self.estado.dec_e),
                         ("401", "409", "7"))
        self.app.calcular("dec")
        self.assertEqual(self.estado.dec_resultado.mensaje, "AB")

    def test_espacios_y_relleno(self):
        for mensaje in (" Hola  123! ", " Hola  12! ", " ", "  "):
            with self.subTest(mensaje=repr(mensaje)):
                self.estado.enc_mensaje = mensaje
                self.app.calcular("enc")
                self.app.transferir()
                self.app.calcular("dec")
                self.assertEqual(self.estado.dec_resultado.mensaje, mensaje)

    def test_error_retira_el_resultado_anterior_y_se_puede_corregir(self):
        self.app.cargar_ejemplo("enc")
        self.app.calcular("enc")
        self.estado.enc_mensaje = "año"
        self.app.calcular("enc")
        self.assertNotIn("enc_resultado", self.estado)
        self.assertIn("Carácter no admitido", self.estado.enc_error)
        self.app.cargar_ejemplo("enc")
        self.app.calcular("enc")
        self.assertNotIn("enc_error", self.estado)
        self.assertEqual(self.estado.enc_resultado.mensaje, "RSA")

    def test_longitud_inconsistente_sin_resultado(self):
        self.app.cargar_ejemplo("dec")
        self.app.calcular("dec")
        self.estado.dec_longitud = "5"
        self.app.calcular("dec")
        self.assertNotIn("dec_resultado", self.estado)
        self.assertIn("no es coherente", self.estado.dec_error)

    def test_editar_entrada_invalida_resultado(self):
        self.app.cargar_ejemplo("enc")
        self.app.calcular("enc")
        self.app.transferir()
        self.app.invalidar("enc")
        self.assertNotIn("enc_resultado", self.estado)
        self.assertNotIn("transferido", self.estado)
        self.assertEqual(self.estado.dec_cifrado, "026054 123875")

    def test_sesiones_no_comparten_datos(self):
        self.app.cargar_ejemplo("enc")
        self.app.calcular("enc")
        self.streamlit.session_state = Estado()
        self.app.inicializar()
        self.assertEqual(self.streamlit.session_state.enc_mensaje, "")
        self.assertNotIn("enc_resultado", self.streamlit.session_state)


if __name__ == "__main__":
    unittest.main()
