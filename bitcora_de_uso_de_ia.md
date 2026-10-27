# Bitácora de uso de Inteligencia Artificial

## 1. ¿Qué le pedimos a la IA?

Usamos la IA como apoyo para agregar a MiniPy los números decimales (`float`), los operadores `/` y `**`, y las funciones `sqrt`, `sin` y `cos`. En específico le pedimos:

* Reconocer decimales en `lexico.py` bajo el token `NUM` y agregar `"**"` y `"/"`.

* Distinguir en `sintactico.py` entre una variable (`Var`) y una función (`Llamada`) viendo si después de `ID` sigue `"("`, además de ajustar `mostrar()` para que acepte valores `float`.

* Atrapar en `interprete.py` todos los errores nuevos para que nunca salga un *traceback* de Python (división entre cero con `/` y `0 ** -1`, raíces de negativos, resultados complejos como `(-2) ** 0.5`, flotantes en `range` y desbordamientos `inf`/`nan`).

## 2. ¿En qué se equivocó y cómo lo detectamos?

### Error 1: Inventó una jerarquía de operaciones para `**`

* **Qué hizo mal:** Sin que se lo especificáramos, la IA creó dos funciones nuevas en la gramática (`potencia` y `primario`) y sus métodos en `sintactico.py` para que `**` tuviera más prioridad que `*` y se calculara de derecha a izquierda (`2 ** 3 ** 2 = 512`).

* **Cómo lo detectamos:** Al revisar `sintactico.py` y ver qué había hecho, nos dimos cuenta de que había agregado una función extra que permitía la jerarquía de operaciones.

* **Cómo lo corregimos:** Borramos las reglas nuevas que inventó la IA y metimos `"/"` y `"**"` directamente en `termino`, al mismo nivel que `"*"` y evaluándose de izquierda a derecha (`2 ** 3 ** 2 = 64`).

### Error 2: Aceptó decimales incompletos (`.5`, `3.`) y notación científica (`1e-3`)

* **Qué hizo mal:** La IA programó `lexico.py` para aceptar números sin dígito antes o después del punto (`.5` y `3.`) y números con exponente (`1e-3`).

* **Cómo lo detectamos:** Al revisar el código de léxico, nos dimos cuenta de que los aceptaba.

* **Cómo lo corregimos:** Simplificamos la regla `NUM` en `gramatica.ebnf` a `[ "." digito { digito } ]` y en `lexico.py` obligamos a que después del punto siempre haya al menos un dígito; si no lo hay, lanza `ErrorLexico`.

## 3. ¿Qué sí funcionó bien?

* Las validaciones en `interprete.py` para atrapar `OverflowError`, `inf`, `nan`, números complejos (`isinstance(res, complex)`) y verificar primero si la función existe antes de evaluar su argumento (`x(1 / 0)` reporta función desconocida).