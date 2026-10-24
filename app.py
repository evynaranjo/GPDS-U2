import math
import os

from flask import Flask, render_template_string, request
from suma_lista import suma_lista

app = Flask(__name__)

PAGINA = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Suma de listas</title>
    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 24px;
            background: #eef2ff;
            font-family: Arial, sans-serif;
            color: #1e293b;
        }

        main {
            width: 100%;
            max-width: 540px;
            padding: 36px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 12px 35px #1e293b15;
        }

        h1 { margin-top: 0; }

        p {
            color: #64748b;
            line-height: 1.6;
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
        }

        input {
            width: 100%;
            padding: 14px;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            font-size: 16px;
        }

        button {
            width: 100%;
            margin-top: 18px;
            padding: 14px;
            border: none;
            border-radius: 10px;
            background: #4f46e5;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        .resultado, .error {
            margin-top: 22px;
            padding: 18px;
            border-radius: 10px;
            overflow-wrap: anywhere;
        }

        .resultado {
            background: #dcfce7;
            color: #166534;
        }

        .error {
            background: #fee2e2;
            color: #991b1b;
        }

        small {
            display: block;
            margin-top: 24px;
            color: #64748b;
        }
    </style>
</head>
<body>
    <main>
        <h1>Suma de listas</h1>
        <p>
            Escribe números separados por comas.
            Puedes incluir negativos y decimales con punto.
        </p>

        <form method="post">
            <label for="numeros">Números que deseas sumar</label>
            <input
                id="numeros"
                name="numeros"
                type="text"
                placeholder="Ejemplo: 10, 20, -5, 2.5"
                value="{{ entrada }}"
                aria-describedby="ayuda"
            >
            <p id="ayuda">Si dejas el campo vacío, el resultado será 0.</p>
            <button type="submit">Calcular suma</button>
        </form>

        {% if resultado is not none %}
            <div class="resultado" role="status">
                <strong>Resultado de la suma:</strong> {{ resultado }}
            </div>
        {% endif %}

        {% if error %}
            <div class="error" role="alert">{{ error }}</div>
        {% endif %}

        <small>Proyecto Deploy con Docker · GPDS-U2</small>
    </main>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def inicio():
    entrada = ""
    resultado = None
    error = None

    if request.method == "POST":
        entrada = request.form.get("numeros", "").strip()

        try:
            numeros = (
                [float(valor.strip()) for valor in entrada.split(",")]
                if entrada
                else []
            )

            if not all(math.isfinite(numero) for numero in numeros):
                raise ValueError

            resultado = suma_lista(numeros)

            if not math.isfinite(resultado):
                resultado = None
                raise ValueError

        except (ValueError, TypeError, OverflowError):
            error = (
                "Ingresa números válidos separados por comas, "
                "por ejemplo: 10, 20, -5, 2.5. "
                "Evita valores demasiado grandes."
            )

    return render_template_string(
        PAGINA,
        entrada=entrada,
        resultado=resultado,
        error=error,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
    )
