# Criptografía RSA — versión web y de escritorio

**MM2015 Matemática Discreta 1 · Grupo 1**  
Sebastian Rodas · Fabricio Estrada

Aplicación Python para encriptar y desencriptar parejas de caracteres ASCII mediante
RSA y mostrar el proceso matemático. La versión web utiliza Streamlit; el profesor
puede usarla desde el navegador cuando esté publicada, sin instalar dependencias.
Los algoritmos matemáticos son los mismos que en la aplicación de escritorio.

## Requisitos para ejecutar o publicar

- Python **3.10 o superior**; se recomienda **Python 3.12** para el despliegue.
- Versión web: `streamlit==1.51.0`, declarada en `requirements.txt`.
- Escritorio opcional: CustomTkinter, Pillow y Tkinter.
- El visitante de la versión publicada solo necesita un navegador con conexión.

## Instalación y ejecución web

Extraer el ZIP y abrir la terminal en la carpeta que contiene `app.py`:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit indica la dirección local que debe abrirse en el navegador,
normalmente `http://localhost:8501`. Mantener abierta esa terminal mientras se usa.
En macOS/Linux puede ser necesario usar `python3` en lugar de `python`.
Para que el profesor acceda sin que nuestra computadora esté encendida, publicar
la aplicación siguiendo `PUBLICAR_WEB.md`; la dirección localhost no sirve para compartirla.

## Cómo usar la aplicación

### Encriptar

1. Pulsar **Cargar ejemplo** o ingresar un mensaje y los valores p, q y e.
2. Pulsar **Encriptar**.
3. Los indicadores muestran n, φ(n), L y si se agregó relleno. También se muestra
   la llave pública (e, n).
4. **Mensaje cifrado C** contiene bloques de seis dígitos separados por un espacio.
   El botón de copia del bloque permite copiar C. **Descargar C y L** guarda
   ambos datos, además de la llave pública, en un archivo de texto.
5. **ASCII** muestra los códigos de tres dígitos y marca el relleno.
   **Bloques** muestra m antes y c después de encriptar.
6. **Usar en Desencriptar →** llena C, L, p, q y e. Después hay que abrir la
   pestaña principal **Desencriptar** y pulsar **Desencriptar**.
   El botón transfiere datos; no cambia automáticamente la pestaña.

### Desencriptar

1. Ingresar C, L y los mismos p, q y e, transferirlos desde Encriptar o cargar el ejemplo.
2. Pulsar **Desencriptar**.
3. Se muestran n, φ(n), d, L, relleno, llave privada (d, n) y el mensaje recuperado M.
4. **Ver espacios** sustituye visualmente cada espacio por ␣; no cambia el mensaje.
5. **Descargar mensaje original** guarda los bytes ASCII del mensaje, incluyendo
   los espacios del inicio y del final, sin agregar saltos de línea.
6. **ASCII** y **Bloques** muestran la conversión inversa y los valores c → m.

Al modificar una entrada se oculta el resultado anterior de esa operación.
Los errores de validación aparecen junto al formulario. Cada visitante tiene
su propia sesión; recargar la página puede reiniciar los datos.

### Comprobaciones

Pulsar **Ejecutar comprobaciones** para ver los veinte casos con su resultado.
Los casos incluyen longitudes pares e impares, signos, espacios, ceros iniciales
y rechazo de entradas inválidas.

## Fundamento y relleno

- p y q deben ser primos distintos; n = p × q y φ(n) = (p − 1)(q − 1).
- Se exige 126126 < n < 1000000; e > 1 y MCD(e, φ(n)) = 1.
- No se exige que e sea primo ni menor que φ(n).
- Cada carácter tiene código ASCII entre 32 y 126, representado con tres dígitos.
- Dos caracteres forman un bloque: AB → 065066.
- L cuenta todos los caracteres originales, incluyendo los espacios.
- Si L es impar se agrega exactamente un espacio ASCII 032 como relleno.
- Encriptar: c = m^e mod n. Desencriptar: m = c^d mod n.
- d es el inverso de e módulo φ(n), con 1 ≤ d < φ(n).
- Para k bloques, L solo puede ser 2k o 2k − 1. Si L es impar se verifica que el
  último carácter sea un espacio y se retira solamente ese carácter.
- No se aplica `strip()` al mensaje original ni al recuperado. L se guarda aparte de C.
- No se admiten tildes, ñ, emojis, tabulaciones ni saltos de línea en el mensaje.
  Se rechazan sin sustituirlos ni eliminarlos.

## Ejemplos completos

| Dato | Ejemplo oficial | Ejemplo con espacios |
|---|---|---|
| Mensaje (entre comillas) | `"RSA"` | `" Hola  123! "` |
| p, q, e | 367, 373, 17 | 367, 373, 17 |
| n, φ(n) | 136891, 136152 | 136891, 136152 |
| L | 3 | 12 |
| Relleno | Un espacio | Ninguno |
| Bloques m | 082083 065032 | 032072 111108 097032 032049 050051 033032 |
| C | 026054 123875 | 087228 073246 021860 098048 108743 127769 |
| d | 8009 | 8009 |
| M recuperado | `"RSA"` | `" Hola  123! "` |

Las comillas no se ingresan. En el segundo ejemplo hay un espacio inicial,
dos entre Hola y 123!, y uno final. Con Ver espacios aparece `␣Hola␣␣123!␣`.

## Algoritmos propios

Todos se encuentran en `rsa_core/matematica.py`:

| Algoritmo | Función | Implementación |
|---|---|---|
| Primalidad | es_primo | División de prueba hasta la raíz cuadrada |
| MCD | mcd | Algoritmo de Euclides |
| Inverso modular | inverso_modular / euclides_extendido | Euclides extendido |
| Exponenciación modular | exp_modular | Cuadrados y multiplicación, reduciendo durante el cálculo |

La lógica RSA no usa `math.gcd`, `pow` modular ni bibliotecas de criptografía.
En una prueba unitaria se compara con potencias completas pequeñas únicamente
como referencia de prueba; la aplicación siempre usa `exp_modular`.

## Comprobaciones y pruebas

```bash
python -m unittest discover -s tests -v
```

- `tests/test_rsa.py`: siete pruebas de algoritmos y RSA. Incluyen los veinte
  casos de la pestaña y la recuperación de los 95 caracteres ASCII imprimibles.
- `tests/test_web_callbacks.py`: siete pruebas de los callbacks con un estado
  simulado: transferencia, parámetros distintos, espacios, errores y sesiones.
- `tests/test_web_ui.py`: tres pruebas de la interfaz con Streamlit AppTest.
  Requieren instalar `requirements.txt`; si falta Streamlit se indican como omitidas.

El conjunto de 95 caracteres está en la prueba unitaria, no en los veinte casos
que muestra la pestaña Comprobaciones.

## Estructura

```text
app.py                      Punto de entrada web
requirements.txt            Dependencias web
.streamlit/config.toml      Tema y configuración web
PUBLICAR_WEB.md              Pasos para obtener el enlace público
ENLACE_WEB.txt               Lugar para registrar el enlace definitivo
GUIA_VIDEO_WEB.md            Recorrido para grabar la versión web
rsa_core/                   Matemática, RSA y comprobaciones compartidas
assets/logo_uvg.png          Logo, cargado con ruta relativa al proyecto
main.py                     Punto de entrada de escritorio (opcional)
requirements-desktop.txt    Dependencias de escritorio
ui/                         Interfaz original de escritorio
README_ESCRITORIO.md         Manual original, con nota sobre dependencias
VIDEO.txt                   Completar con el enlace real del video o indicar el MP4
tests/                      Pruebas automáticas
```

## Escritorio opcional

```bash
python -m pip install -r requirements-desktop.txt
python main.py
```

Tkinter debe estar disponible. En Linux puede requerir instalar `python3-tk`.
El despliegue web no importa la carpeta ui ni necesita CustomTkinter o Tkinter.

## Entrega

Completar el enlace web y el video. Comprimir toda la carpeta como
`Grupo_No.1_Proyecto.zip`. Mantener el README, los recursos, los algoritmos y
las dependencias. El video o su enlace accesible se indica en `VIDEO.txt`.
No se requiere un informe adicional.
