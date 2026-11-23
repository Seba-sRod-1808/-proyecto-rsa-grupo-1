> Manual de la interfaz original de escritorio. Para la versión web, consultar README.md.

# Proyecto de criptografía RSA — MM2015 Matemática Discreta 1

Aplicación de escritorio en Python para **encriptar y desencriptar** mensajes de texto con RSA,
por bloques de dos caracteres ASCII, mostrando el detalle de cada paso.

**Grupo 1**

- Sebastian Rodas
- Fabricio Estrada

## Requisitos

- **Python 3.10 o superior** (probado con Python 3.12).
- Tkinter (incluido con Python en Windows y macOS; en Linux: `sudo apt install python3-tk`).
- Bibliotecas externas, listadas en `requirements-desktop.txt`:
  - **CustomTkinter**: componentes de la interfaz gráfica.
  - **Pillow**: carga del logo de la universidad.

## Instalación y ejecución

```bash
pip install -r requirements-desktop.txt
python main.py
```

En macOS/Linux puede ser `python3` en lugar de `python`.
Pruebas automáticas (opcional): `python -m unittest discover -s tests`

## Uso

La ventana tiene tres pestañas. En cualquier campo, `Enter` ejecuta la operación y
**Cargar ejemplo** llena los datos del ejemplo de referencia.

### Encriptar
1. Escriba el mensaje y los valores **p**, **q** y **e**. Mientras escribe, la aplicación muestra
   **L**, si se agregará relleno, y los valores de **n** y **φ**, o el motivo por el que p, q o e no
   son válidos.
2. Presione **Encriptar**.
3. Resultados:
   - Fila superior: **n**, **φ**, **L**, **relleno** y **llave pública (e, n)**.
   - Tarjeta **«Mensaje cifrado C»**: el cifrado **C** (bloques de 6 dígitos separados por un
     espacio) y, debajo, **L** y el mensaje con relleno cuando corresponde.
   - Pestaña **ASCII**: cada carácter con su código de tres dígitos. El espacio se muestra como `␣`
     y el de relleno aparece resaltado.
   - Pestaña **Bloques**: cada pareja con su bloque **m** antes de encriptar y **c** después.
4. **Copiar C** lo copia al portapapeles. **Usar en Desencriptar →** lleva C, L, p, q y e a la
   pestaña Desencriptar.

### Desencriptar
1. Escriba **C** tal como se obtuvo (por ejemplo `026054 123875`), la longitud **L** y los mismos
   **p**, **q** y **e**, o use el botón «Usar en Desencriptar →». Bajo C se indican los valores de
   L coherentes con la cantidad de bloques.
2. Presione **Desencriptar**.
3. Resultados: **n**, **φ**, **d**, **L**, relleno, **llave privada (d, n)** y el **mensaje
   recuperado M**. La casilla **Ver espacios** muestra los espacios como `␣` para comprobar los del
   inicio y del final. Las pestañas **Bloques** (c → m) y **ASCII** (código → carácter) muestran el
   detalle.

### Comprobaciones
El botón **Ejecutar** corre los 20 casos descritos al final y muestra el resultado de cada uno.

## Funcionamiento del relleno

- **L** es la cantidad de caracteres del mensaje original, contando todos sus espacios.
- Si **L es impar**, se agrega **exactamente un espacio** (ASCII 032) al final para completar la
  última pareja. Ejemplo: `"RSA"` (L = 3) → `"RSA "` → bloques `082083 065032`.
- Al desencriptar con **L impar**, se verifica que el último carácter recuperado sea un espacio y
  se retira **solo ese carácter**; no se usa `strip()`, de modo que los espacios originales del
  inicio y del final se conservan. Con **L par** no se retira nada.
- L no forma parte de C, por eso se muestra y debe ingresarse por separado.

## Ejemplo completo

| Dato | Valor |
|---|---|
| Mensaje | `RSA` |
| p, q, e | 367, 373, 17 |
| n, φ | 136891, 136152 (MCD(17, 136152) = 1) |
| L y relleno | L = 3 → `"RSA "` |
| Bloques m | `082083 065032` |
| Cifrado C | `026054 123875` |
| d | 8009 |
| Mensaje recuperado | `RSA` |

## Estructura del proyecto

```
main.py                    Punto de entrada
requirements-desktop.txt           Dependencias
assets/logo_uvg.png        Logo de la universidad
rsa_core/
    matematica.py          Algoritmos matemáticos propios
    rsa.py                 Validaciones, encriptación y desencriptación
    comprobaciones.py      Casos de prueba del enunciado
ui/
    app.py                 Ventana principal
    vistas.py              Pestañas Encriptar, Desencriptar y Comprobaciones
    componentes.py         Componentes visuales y paleta de colores
tests/test_rsa.py          Pruebas automáticas (unittest)
```

Los recursos se cargan con rutas relativas construidas con `os.path.join`, por lo que el proyecto
funciona desde cualquier carpeta.

## Algoritmos matemáticos

Implementados en **`rsa_core/matematica.py`**, sin `math.gcd`, sin `pow` con módulo y sin
bibliotecas de criptografía:

| Algoritmo | Función | Uso |
|---|---|---|
| Primalidad | `es_primo(n)` | Validar p y q (división de prueba hasta √n) |
| Máximo común divisor | `mcd(a, b)` | Validar MCD(e, φ) = 1 (algoritmo de Euclides) |
| Inverso modular | `inverso_modular(a, m)` y `euclides_extendido(a, b)` | Obtener d con 1 ≤ d < φ |
| Exponenciación modular | `exp_modular(base, exponente, modulo)` | c = mᵉ mod n y m = cᵈ mod n, por cuadrado y multiplicación, reduciendo módulo n en cada paso |

## Comprobaciones realizadas

Disponibles en la pestaña **Comprobaciones** y en `tests/test_rsa.py`:

- Ejemplo de referencia del enunciado: n, φ, bloques, C, d y M exactos.
- Recuperación exacta con longitud par e impar, un solo carácter, mayúsculas y minúsculas, números
  y signos, espacios consecutivos, espacios al inicio y al final, cifrados con ceros iniciales y los
  95 caracteres ASCII imprimibles.
- Rechazo, con un mensaje claro, de: p no primo, p = q, n fuera de rango, e no coprimo con φ,
  e no entero, carácter no admitido (ñ), bloque de C con 5 dígitos o con letras, bloque c ≥ n,
  L inconsistente con la cantidad de bloques y L impar sin espacio de relleno.

Ante un dato inválido, el error aparece en rojo bajo el formulario y en la barra inferior, y se
borran los resultados anteriores para no presentar una salida incorrecta como válida.

## Video demostrativo

Ver `VIDEO.txt`.
