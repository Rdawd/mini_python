# Especificación de la extensión de MiniPy

El trabajo fue realizado como parte del curso de **Teoría de la computación**. El siguiente documento contiene las especificaciones de los cambios hechos a `lexico.py`, `interprete.py`, y `sintactico.py`. Se agregaron decimales, división `/`, potencia `**`, funciones `sqrt`, `sin` y `cos`.

El equipo de desarrollo esta conformado por: Rodrigo Castillo Guerrero, Jesús Enrique Castro Puppo, Adrián Javier Ramirez Pérez y  Nickole Isabella Domínguez Mesta.

## Especificación

Se agregaron: Números decimales (`3.14`), división real (`7 / 2` vale `3.5`), potencia (`2 ** 3` vale `8`), las funciones `sqrt(16)`, `sin(0)` y `cos(0)`.

**Valores.** Hay dos clases de valores: enteros, sin límite de tamaño, y decimales. Los decimales si tienen limite de tamaño y es: 1.7976931348623157e+308. Debido a que después de ese numero se convierte en un inf y daría un error por no aceptar esa clase de valor.

**Literales.** Un número es una cadena de dígitos, o dígitos, un punto y más dígitos.

- Válidos: `0`, `7`, `3.14`, `0.5`, `0.0`, `10.25`. No hay límite de dígitos: un literal con 400 decimales se acepta y se redondea (imprime `0.1111111111111111`). Uno demasiado pequeño, como un cero, el punto, cuatrocientos ceros y un uno, se redondea a `0.0` sin error.
- Error léxico: `3.` (número incompleto, falta un dígito después del punto); `.5` y `1.2.3` (carácter inesperado `'.'`), `007` y `07.5` (un número no puede empezar con cero después tener un digito y seguir con punto decimal; `0` y `0.5` sí valen).
- No hay notación científica: `1e-3` no es un número. 

**Enteros y decimales juntos.** Si algún operando es decimal, el resultado es decimal. Las comparaciones comparan valores: `2 == 2.0` es verdadero. La comparación es exacta, así que `0.1 + 0.2 == 0.3` es falso (`0.1 + 0.2` vale `0.30000000000000004`).

**Operadores, precedencia y asociatividad.** De menor a mayor precedencia:

1. `+` y `-` binarios: asocian a la izquierda. `10 - 4 - 3` vale `3`.
2. `*`, `/`, `//`, `%` y `**`: los cinco están en el mismo nivel y asocian a la izquierda. `**` no tiene un nivel propio: `2 ** 3 ** 2` es `(2 ** 3) ** 2` y vale `64`; `2 * 3 ** 2` vale `36`; `2 ** 3 * 2` vale `16`; `8 / 2 // 3` es `(8 / 2) // 3`.
3. Paréntesis: lo de adentro se calcula primero y permite cambiar el orden. `2 ** (3 ** 2)` vale `512`; `-(2 ** 2)` vale `-4`; `(2 + 3) * 4` vale `20`.

Sin cambio: en una operación binaria se evalúa primero el operando izquierdo y después el derecho. En `y + 1 / 0`, si `y` no tiene valor, ese es el error que aparece, no la división entre cero.

**División `/`.** División real: el resultado siempre es decimal, aunque sea exacta. `7 / 2` vale `3.5`, `8 / 2` vale `4.0`, `-7 / 2` vale `-3.5`. Un divisor `0` o `0.0` es error: «división entre cero».

**Potencia `**`.** Un entero elevado a un entero no negativo da un entero exacto (`2 ** 100` vale `1267650600228229401496703205376`). Un exponente negativo o decimal da un decimal: `2 ** -1` vale `0.5` y `4 ** 0.5` vale `2.0`. `0 ** 0` vale `1`.

- `0 ** -1` (o `0.0 ** -1`): error, división entre cero.
- Base negativa con exponente no entero, como `(-2) ** 0.5`: el resultado sería complejo y MiniPy no tiene complejos. Error: raíz o potencia de número negativo.
- Resultado que no cabe en un decimal: error, desbordamiento numérico.

**Desbordamiento.** Es error de ejecución («desbordamiento numérico») cualquier operación o función cuyo resultado sea infinito o no sea un número, o que obligue a convertir un entero demasiado grande a decimal. `10 ** 308 * 1.0` vale `1e+308`, pero `10 ** 309 * 1.0`, `10.0 ** 308 * 10` y `10.0 ** 400` son error.

**Funciones `sqrt`, `sin` y `cos`.** Reciben un argumento, que puede ser cualquier expresión, y devuelven siempre un decimal. `sin` y `cos` trabajan en radianes. Se pueden anidar: `sqrt(3 * 3 + 4 * 4)` vale `5.0` y `cos(sin(0))` vale `1.0`.

- No son palabras reservadas, son identificadores: una llamada es un identificador seguido de `(`. Se puede tener una variable llamada `sqrt` (después de `sqrt = 5`, `sqrt(16)` sigue siendo la función); `sin` sin paréntesis es una variable que no tiene valor.
- Errores de ejecución: `sqrt` de un negativo («raíz cuadrada de número negativo»); un nombre que no es función («función desconocida: 'foo'»), que se revisa antes de evaluar el argumento, así que `foo(1 / 0)` da función desconocida; un argumento que desborda (`sin(10 ** 400)`).
- Errores sintácticos: llamada sin argumento (`sin()`), con dos (`sqrt(4, 2)`) o sin cerrar el paréntesis.

**Resumen de errores nuevos.**

- Léxicos: número incompleto (`3.`); carácter inesperado `'.'` (`.5`, `1.2.3`); cero a la izquierda (`007`, `07.5`).
- Sintácticos: `1e-3`; `elif` fuera de lugar o mal formado; llamada a función mal formada.
- De ejecución: división entre cero; raíz o potencia de número negativo; desbordamiento numérico; raíz cuadrada de número negativo; función desconocida; range solo admite enteros; variable sin valor.
