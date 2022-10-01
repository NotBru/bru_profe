PRECIO_LECHUGA = 0.421
PRECIO_TOMATE = 0.213
PRECIO_SANDÍA = 113

def calcular_monto(cant_lechuga, cant_tomate, cant_sandía):

    monto_lechuga = cant_lechuga * PRECIO_LECHUGA
    monto_tomate = cant_tomate * PRECIO_TOMATE
    monto_sandía = cant_sandía * PRECIO_SANDÍA

    monto_total = monto_lechuga + monto_tomate + monto_sandía

    if cant_lechuga >= 500 and cant_tomate >= 500 and cant_sandía >= 1:
        monto_total *= 0.85
    elif cant_tomate >= 1000:
        monto_total -= monto_tomate * 0.1

    return monto_total

def atender_un_cliente():

    print("¡Bienvenide!")
    cant_lechuga = float(input("Cantidad de lechuga [g]: "))
    cant_tomate = float(input("Cantidad de tomate [g]: "))
    cant_sandía = float(input("Cantidad de sandía [kg]: "))

    monto = calcular_monto(cant_lechuga, cant_tomate, cant_sandía)

    print("Le va a costar:", monto)

atender_un_cliente()
