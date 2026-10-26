"""
Intérprete de MiniPy: recorre el AST y lo ejecuta.

Las variables se guardan en un diccionario {nombre: valor}.
Hay dos funciones, una para cada clase de nodo:
  ejecutar() para sentencias (no devuelven nada)
  evaluar()  para expresiones y condiciones (devuelven un valor)

Uso: python interprete.py programa.py
"""

# >>> NUEVO [SQRT]: math, para sqrt, sin y cos.
import math
import sys
from lexico import analizar, leer_o_salir, ErrorLexico
from sintactico import (Parser, ErrorSintactico, Asignacion, Imprimir, Si, Para,
                        BinOp, Condicion, Negativo, Num, Var, Llamada)
# >>> MODIFICADO [SQRT]: se importa también Llamada.

OPERACIONES = {
    "+":  lambda a, b: a + b,
    "-":  lambda a, b: a - b,
    "*":  lambda a, b: a * b,
    # >>> NUEVO [ARITMÉTICO / **]: división real (siempre da float).
    "/":  lambda a, b: a / b,
    "//": lambda a, b: a // b,
    "%":  lambda a, b: a % b,
    # >>> NUEVO [ARITMÉTICO / **]: potencia.
    "**": lambda a, b: a ** b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<":  lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
}

# >>> NUEVO [SQRT]: funciones predefinidas (sin y cos en radianes).
FUNCIONES = {
    "sqrt": math.sqrt,
    "sin":  math.sin,
    "cos":  math.cos,
}


class ErrorEjecucion(Exception):
    pass


def ejecutar(sentencias, variables):
    for s in sentencias:
        if isinstance(s, Asignacion):
            variables[s.nombre] = evaluar(s.valor, variables)

        elif isinstance(s, Imprimir):
            print(evaluar(s.valor, variables))

        elif isinstance(s, Si):
            if evaluar(s.condicion, variables):
                ejecutar(s.entonces, variables)
            else:
                ejecutar(s.sino, variables)

        elif isinstance(s, Para):
            inicio = evaluar(s.inicio, variables)   # los límites se evalúan
            fin = evaluar(s.fin, variables)         # una sola vez, como en Python
            # >>> NUEVO [FLOAT]: range solo admite enteros (evita el error de Python).
            if isinstance(inicio, float) or isinstance(fin, float):
                raise ErrorEjecucion("range solo admite enteros")
            for i in range(inicio, fin):
                variables[s.variable] = i
                ejecutar(s.cuerpo, variables)

        else:
            # Si se agrega un nodo al parser y se olvida aquí, mejor fallar
            # que ignorar la sentencia en silencio
            raise ErrorEjecucion(f"sentencia desconocida: {type(s).__name__}")


def evaluar(e, variables):
    if isinstance(e, Num):
        # >>> NUEVO [FLOAT]: un decimal gigante se vuelve inf; se rechaza.
        if isinstance(e.valor, float) and math.isinf(e.valor):
            raise ErrorEjecucion("desbordamiento numérico")
        return e.valor

    if isinstance(e, Var):
        if e.nombre not in variables:
            raise ErrorEjecucion(f"la variable '{e.nombre}' no tiene valor")
        return variables[e.nombre]

    if isinstance(e, Negativo):
        return -evaluar(e.valor, variables)

    # >>> NUEVO [SQRT]: llamada a función. 1) ¿existe? 2) calcular el argumento
    #   3) sqrt de negativo = error 4) overflow, inf o nan = error.
    if isinstance(e, Llamada):
        if e.nombre not in FUNCIONES:
            raise ErrorEjecucion(f"función desconocida: '{e.nombre}'")
        arg = evaluar(e.arg, variables)
        if e.nombre == "sqrt" and arg < 0:
            raise ErrorEjecucion("raíz cuadrada de número negativo")
        try:
            res = FUNCIONES[e.nombre](arg)
        except OverflowError:
            raise ErrorEjecucion("desbordamiento numérico")
        if math.isinf(res) or math.isnan(res):
            raise ErrorEjecucion("desbordamiento numérico")
        return res

    if isinstance(e, (BinOp, Condicion)):   # misma forma: op, izq, der
        a = evaluar(e.izq, variables)
        b = evaluar(e.der, variables)
        # >>> MODIFICADO [ARITMÉTICO / **]: "/" también da error si el divisor es 0.
        if e.op in ("/", "//", "%") and b == 0:
            raise ErrorEjecucion("división entre cero")
        # >>> NUEVO [ARITMÉTICO / **]: 0 ** negativo equivale a 1 / 0.
        if e.op == "**" and a == 0 and b < 0:
            raise ErrorEjecucion("división entre cero")
        # >>> NUEVO [FLOAT]: si el resultado desborda (OverflowError) se avisa.
        try:
            res = OPERACIONES[e.op](a, b)
        except OverflowError:
            raise ErrorEjecucion("desbordamiento numérico")
        # >>> NUEVO [ARITMÉTICO / **]: (-2) ** 0.5 da un complejo; MiniPy no los tiene.
        if isinstance(res, complex):
            raise ErrorEjecucion("raíz o potencia de número negativo")
        # >>> NUEVO [FLOAT]: resultado inf o nan = desbordamiento numérico.
        if isinstance(res, float) and (math.isinf(res) or math.isnan(res)):
            raise ErrorEjecucion("desbordamiento numérico")
        return res

    raise ErrorEjecucion(f"expresión desconocida: {type(e).__name__}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python interprete.py programa.py")

    # Desde 2022 (Python 3.11, y las correcciones de seguridad 3.10.7, 3.9.14,
    # 3.8.14 y 3.7.14), convertir entre texto y entero con más de 4300 dígitos
    # lanza ValueError: al leer literales y al imprimir. Los enteros del
    # lenguaje no tienen límite, así que se quita. (Otro ejemplo de semántica
    # heredada.)
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)

    try:
        arbol = Parser(analizar(leer_o_salir(sys.argv[1]))).programa()
        ejecutar(arbol.cuerpo, {})
    except ErrorLexico as e:
        sys.exit(f"Error léxico: {e}")
    except ErrorSintactico as e:
        sys.exit(f"Error sintáctico: {e}")
    except ErrorEjecucion as e:
        sys.exit(f"Error de ejecución: {e}")
    except RecursionError:
        # El parser y el intérprete son recursivos y usan la pila de Python.
        # La profundidad del árbol no es la del texto: una suma de 1000
        # términos sin paréntesis da un árbol de profundidad 999.
        sys.exit("Error: el árbol del programa es demasiado profundo "
                 "(mucho anidamiento o una expresión muy larga)")
    except MemoryError:
        # Todo programa termina, pero un número puede crecer más rápido que
        # la memoria: x = x * x duplica en cada vuelta los bits de x. (En
        # Linux, el sistema puede terminar el proceso antes de que Python
        # lance MemoryError.)
        sys.exit("Error de ejecución: se agotó la memoria")
    except KeyboardInterrupt:
        # Todo programa del lenguaje base termina, pero puede tardar muchísimo;
        # con while aparecen los ciclos infinitos. Ctrl+C sin traceback.
        sys.exit("Ejecución interrumpida")