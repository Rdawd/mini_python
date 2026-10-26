def main():
    # Parte 1: cuántos decimales distingue el sistema cerca de 1.
    # Se prueba 1 + 10^-k; mientras 1 + x sea distinto de 1, el sistema
    # todavía "ve" ese decimal. Como x solo se vuelve más pequeño, la
    # última k que cumple es el máximo.
    precision = 0
    for k in range(1, 40):
        x = 1 / (10 ** k)
        if 1 + x != 1:
            precision = k
    print(precision)

    # Parte 2: qué tan lejos del punto puede estar el primer dígito
    # distinto de cero sin que el número se convierta en 0.0.
    lejano = 0
    for k in range(1, 400):
        y = 1 / (10 ** k)
        if y > 0:
            lejano = k
    print(lejano)

main()
