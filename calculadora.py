def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero")
    return a / b


OPS = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide,
}


def main() -> None:
    print("=== Calculadora ===")
    print("Operaciones: +, -, *, /")
    try:
        a = float(input("Primer número: "))
        op = input("Operación: ").strip()
        b = float(input("Segundo número: "))
        if op not in OPS:
            print(f"Operación no válida: {op}")
            return
        result = OPS[op](a, b)
        print(f"Resultado: {result}")
    except ValueError:
        print("Debes ingresar números válidos")
    except ZeroDivisionError as e:
        print(e)


if __name__ == "__main__":
    main()