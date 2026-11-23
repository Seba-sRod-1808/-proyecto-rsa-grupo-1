"""Pruebas de la interfaz real con AppTest cuando Streamlit está instalado."""
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
try:
    from streamlit.testing.v1 import AppTest
except ModuleNotFoundError as error:
    if error.name != "streamlit":
        raise
    AppTest = None


@unittest.skipIf(AppTest is None, "Instalar requirements.txt para ejecutar AppTest")
class TestInterfazWeb(unittest.TestCase):
    def setUp(self):
        self.at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=15).run()
        self.assertFalse(self.at.exception)

    def test_recorrido_completo_y_comprobaciones(self):
        self.at.button(key="ejemplo_enc").click().run()
        self.at.button(key="calcular_enc").click().run()
        self.assertFalse(self.at.exception)
        self.assertIn("026054 123875", [c.value for c in self.at.code])
        self.at.button(key="transferir").click().run()
        self.assertEqual(self.at.text_input(key="dec_longitud").value, "3")
        self.at.button(key="calcular_dec").click().run()
        self.assertFalse(self.at.exception)
        self.assertEqual(self.at.session_state["dec_resultado"].mensaje, "RSA")
        self.at.button(key="comprobar").click().run()
        self.assertTrue(any(s.value == "20 de 20 superadas" for s in self.at.success))

    def test_espacios_error_y_recuperacion(self):
        mensaje = " Hola  12! "
        self.at.text_area(key="enc_mensaje").input(mensaje).run()
        self.at.button(key="calcular_enc").click().run()
        self.at.button(key="transferir").click().run()
        self.at.button(key="calcular_dec").click().run()
        self.at.checkbox(key="ver_espacios").check().run()
        self.assertIn(mensaje.replace(" ", "␣"), [c.value for c in self.at.code])
        self.at.text_area(key="enc_mensaje").input("año").run()
        self.at.button(key="calcular_enc").click().run()
        self.assertFalse(self.at.exception)
        self.assertTrue(any("Carácter no admitido" in e.value for e in self.at.error))
        self.at.button(key="ejemplo_enc").click().run()
        self.at.button(key="calcular_enc").click().run()
        self.assertFalse(self.at.error)

    def test_longitud_invalida_y_limpieza_al_editar(self):
        self.at.button(key="ejemplo_dec").click().run()
        self.at.button(key="calcular_dec").click().run()
        self.at.text_input(key="dec_longitud").input("5").run()
        self.assertNotIn("RSA", [c.value for c in self.at.code])
        self.at.button(key="calcular_dec").click().run()
        self.assertFalse(self.at.exception)
        self.assertTrue(any("no es coherente" in e.value for e in self.at.error))


if __name__ == "__main__":
    unittest.main()
