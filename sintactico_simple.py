"""
Esqueleto del analizador sintáctico de MiniPy, sin ninguna protección.
Una función por cada regla de gramatica.ebnf, que aparece como comentario.

El árbol se arma con tuplas: un número es un int o float, una variable es un str,
y todo lo demás es (operación, partes...).

Uso: python sintactico_simple.py programa.py
"""
import sys
from pprint import pprint
from lexico_simple import analizar

tokens = []                    # la lista que entrega el léxico
pos = 0                        # el token que se está viendo


def ver(*tipos):
    """¿El token actual es de alguno de estos tipos?"""
    return tokens[pos][0] in tipos


def consumir(*tipos):
    """Exige un token de alguno de estos tipos, avanza y devuelve su valor."""
    global pos
    if not ver(*tipos):
        tipo, valor = tokens[pos]
        raise SyntaxError(f"se esperaba {' o '.join(tipos)}, "
                          f"se encontró {valor or tipo}")
    pos += 1
    return tokens[pos - 1][1]


# programa ::= "def" "main" "(" ")" ":" bloque "main" "(" ")" NEWLINE
def programa():
    for t in ("DEF", "MAIN", "(", ")", ":"):
        consumir(t)
    cuerpo = bloque()
    for t in ("MAIN", "(", ")", "NEWLINE", "EOF"):
        consumir(t)
    return cuerpo


# bloque ::= NEWLINE INDENT sentencia { sentencia } DEDENT
def bloque():
    consumir("NEWLINE")
    consumir("INDENT")
    sentencias = [sentencia()]
    while not ver("DEDENT"):
        sentencias.append(sentencia())
    consumir("DEDENT")
    return sentencias


# sentencia ::= asignacion | si | para | imprimir
def sentencia():
    if ver("IF"):
        return si()
    if ver("FOR"):
        return para()
    if ver("PRINT"):
        return imprimir()
    return asignacion()


# asignacion ::= ID "=" expr NEWLINE
def asignacion():
    nombre = consumir("ID")
    consumir("=")
    valor = expr()
    consumir("NEWLINE")
    return ("=", nombre, valor)


# imprimir ::= "print" "(" expr ")" NEWLINE
def imprimir():
    consumir("PRINT")
    consumir("(")
    valor = expr()
    consumir(")")
    consumir("NEWLINE")
    return ("print", valor)


# si ::= "if" condicion ":" bloque [ "else" ":" bloque ]
def si():
    consumir("IF")
    cond = condicion()
    consumir(":")
    entonces = bloque()
    sino = []
    if ver("ELSE"):
        consumir("ELSE")
        consumir(":")
        sino = bloque()
    return ("if", cond, entonces, sino)


# para ::= "for" ID "in" "range" "(" expr [ "," expr ] ")" ":" bloque
def para():
    consumir("FOR")
    variable = consumir("ID")
    consumir("IN")
    consumir("RANGE")
    consumir("(")
    inicio, fin = 0, expr()            # range(b) es range(0, b)
    if ver(","):
        consumir(",")
        inicio, fin = fin, expr()
    consumir(")")
    consumir(":")
    return ("for", variable, inicio, fin, bloque())


# condicion ::= expr OPREL expr
def condicion():
    izq = expr()
    op = consumir("==", "!=", "<", "<=", ">", ">=")
    return (op, izq, expr())


# expr ::= termino { ( "+" | "-" ) termino }
def expr():
    nodo = termino()
    while ver("+", "-"):
        op = consumir("+", "-")
        nodo = (op, nodo, termino())   # asociatividad izquierda
    return nodo


# termino ::= factor { ( "*" | "/" | "//" | "%" | "**" ) factor }
# >>> MODIFICADO (A, B): se agregaron "/" y "**" a la lista de operadores.
#   Por qué: no se pidió jerarquía especial, así que "**" se trata como
#   cualquier otro operador de este nivel (igual que "*"): se aplican de
#   izquierda a derecha. Ejemplo: 2 ** 3 ** 2 se lee (2 ** 3) ** 2 = 64.
def termino():
    nodo = factor()
    while ver("*", "/", "//", "%", "**"):
        op = consumir("*", "/", "//", "%", "**")
        nodo = (op, nodo, factor())
    return nodo


# factor ::= NUM | ID [ "(" expr ")" ] | "(" expr ")" | "-" factor
# >>> MODIFICADO (A, C): dos cambios dentro de factor, el resto igual:
#   - NUM: devuelve float si el lexema tiene "."; si no, int (antes: siempre int).
#   - ID: si después viene "(" es una llamada a función, p. ej. ("sqrt", arg)
#     (antes: devolvía solo el nombre). Es LL(1): se consume ID y se mira
#     UN token más. sqrt, sin y cos no son reservadas; son ID comunes.
def factor():
    if ver("NUM"):
        lexema = consumir("NUM")
        if "." in lexema:
            return float(lexema)
        return int(lexema)
    if ver("ID"):
        nombre = consumir("ID")
        if ver("("):
            consumir("(")
            arg = expr()
            consumir(")")
            return (nombre, arg)
        return nombre
    if ver("-"):
        consumir("-")
        return ("neg", factor())
    consumir("(")
    nodo = expr()
    consumir(")")
    return nodo


if __name__ == "__main__":
    # utf-8-sig acepta el BOM que agregan algunos editores de Windows
    tokens = analizar(open(sys.argv[1], encoding="utf-8-sig").read())
    pprint(programa(), width=60)