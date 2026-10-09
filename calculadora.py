import ast
import operator
import tkinter as tk


class CalculadoraIOS:
    FONDO = "#000000"
    NUMERO = "#333333"
    FUNCION = "#A5A5A5"
    NARANJA = "#FF9F0A"

    def __init__(self, ventana):
        self.ventana = ventana
        self.expresion = ""
        self.resultado_mostrado = False
        self.botones = []

        ventana.title("Calculadora")
        ventana.geometry("375x650")
        ventana.resizable(False, False)
        ventana.configure(bg=self.FONDO)

        self.lienzo = tk.Canvas(
            ventana,
            width=375,
            height=650,
            bg=self.FONDO,
            highlightthickness=0,
        )
        self.lienzo.pack(fill="both", expand=True)

        self.pantalla = self.lienzo.create_text(
            344,
            150,
            text="0",
            fill="white",
            font=("Segoe UI Light", 64),
            anchor="e",
        )

        self.crear_teclado()
        self.lienzo.bind("<Button-1>", self.click)
        self.lienzo.bind("<ButtonRelease-1>", self.soltar)
        ventana.bind("<Key>", self.teclado)

    def crear_teclado(self):
        filas = [
            [("AC", "funcion"), ("±", "signo"), ("%", "porcentaje"), ("÷", "/")],
            [("7", "7"), ("8", "8"), ("9", "9"), ("×", "*")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("−", "-")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("+", "+")],
        ]

        diametro = 76
        centros_x = [52, 142, 232, 322]
        centros_y = [230, 320, 410, 500]

        for fila, centro_y in zip(filas, centros_y):
            for columna, (texto, valor) in enumerate(fila):
                color = self.color_para(texto, columna)
                color_texto = "black" if color == self.FUNCION else "white"
                self.dibujar_boton(
                    centros_x[columna], centro_y, diametro, texto, valor, color, color_texto
                )

        # El cero es una cápsula de doble ancho, como en iOS.
        self.dibujar_capsula(14, 552, 166, 76, "0", "0", self.NUMERO)
        self.dibujar_boton(232, 590, diametro, ",", ".", self.NUMERO, "white")
        self.dibujar_boton(322, 590, diametro, "=", "igual", self.NARANJA, "white")

    def color_para(self, texto, columna):
        if texto in {"AC", "±", "%"}:
            return self.FUNCION
        if columna == 3:
            return self.NARANJA
        return self.NUMERO

    def dibujar_boton(self, cx, cy, diametro, texto, valor, color, color_texto):
        radio = diametro / 2
        figura = self.lienzo.create_oval(
            cx - radio,
            cy - radio,
            cx + radio,
            cy + radio,
            fill=color,
            outline="",
        )
        etiqueta = self.lienzo.create_text(
            cx,
            cy,
            text=texto,
            fill=color_texto,
            font=("Segoe UI", 25),
        )
        self.botones.append(
            {"zona": (cx - radio, cy - radio, cx + radio, cy + radio), "figura": figura,
             "etiqueta": etiqueta, "valor": valor, "color": color}
        )

    def dibujar_capsula(self, x, y, ancho, alto, texto, valor, color):
        radio = alto / 2
        izquierda = self.lienzo.create_oval(x, y, x + alto, y + alto, fill=color, outline="")
        centro = self.lienzo.create_rectangle(
            x + radio, y, x + ancho - radio, y + alto, fill=color, outline=""
        )
        derecha = self.lienzo.create_oval(
            x + ancho - alto, y, x + ancho, y + alto, fill=color, outline=""
        )
        etiqueta = self.lienzo.create_text(
            x + 38,
            y + alto / 2,
            text=texto,
            fill="white",
            font=("Segoe UI", 25),
        )
        self.botones.append(
            {"zona": (x, y, x + ancho, y + alto), "figura": (izquierda, centro, derecha),
             "etiqueta": etiqueta, "valor": valor, "color": color}
        )

    def click(self, evento):
        for boton in self.botones:
            x1, y1, x2, y2 = boton["zona"]
            if x1 <= evento.x <= x2 and y1 <= evento.y <= y2:
                self.iluminar(boton)
                self.accion(boton["valor"])
                break

    def soltar(self, _evento):
        for boton in self.botones:
            self.colorear(boton, boton["color"])

    def iluminar(self, boton):
        colores = {
            self.NUMERO: "#737373",
            self.FUNCION: "#D9D9D9",
            self.NARANJA: "#FFC56B",
        }
        self.colorear(boton, colores[boton["color"]])

    def colorear(self, boton, color):
        figuras = boton["figura"] if isinstance(boton["figura"], tuple) else (boton["figura"],)
        for figura in figuras:
            self.lienzo.itemconfigure(figura, fill=color)

    def accion(self, valor):
        if valor == "funcion":
            self.expresion = ""
        elif valor == "igual":
            self.calcular()
            return
        elif valor == "signo":
            self.cambiar_signo()
        elif valor == "porcentaje":
            self.aplicar_porcentaje()
        else:
            if self.resultado_mostrado and valor not in "+-*/":
                self.expresion = ""
            self.resultado_mostrado = False
            self.expresion += valor

        self.actualizar_pantalla()

    def calcular(self):
        if not self.expresion:
            return
        try:
            resultado = self.evaluar_seguro(self.expresion)
            self.expresion = self.formatear(resultado)
            self.resultado_mostrado = True
        except (ValueError, ZeroDivisionError, SyntaxError):
            self.expresion = "Error"
            self.resultado_mostrado = True
        self.actualizar_pantalla()

    def cambiar_signo(self):
        if not self.expresion:
            return
        try:
            self.expresion = self.formatear(-float(self.expresion))
        except ValueError:
            self.expresion = f"-({self.expresion})"

    def aplicar_porcentaje(self):
        if not self.expresion:
            return
        try:
            self.expresion = self.formatear(float(self.expresion) / 100)
        except ValueError:
            self.expresion = f"({self.expresion})/100"

    def actualizar_pantalla(self):
        texto = self.expresion.replace("*", "×").replace("/", "÷").replace("-", "−") or "0"
        tamano = 64 if len(texto) <= 9 else 45 if len(texto) <= 13 else 32
        self.lienzo.itemconfigure(self.pantalla, text=texto, font=("Segoe UI Light", tamano))

    def teclado(self, evento):
        if evento.char in "0123456789.+-*/":
            self.accion(evento.char)
        elif evento.keysym in {"Return", "KP_Enter"}:
            self.accion("igual")
        elif evento.keysym == "Escape":
            self.accion("funcion")
        elif evento.keysym == "BackSpace":
            self.expresion = self.expresion[:-1]
            self.actualizar_pantalla()

    @staticmethod
    def formatear(numero):
        if isinstance(numero, float) and numero.is_integer():
            return str(int(numero))
        return f"{numero:.10g}" if isinstance(numero, float) else str(numero)

    @staticmethod
    def evaluar_seguro(expresion):
        operaciones = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def evaluar(nodo):
            if isinstance(nodo, ast.Expression):
                return evaluar(nodo.body)
            if isinstance(nodo, ast.Constant) and type(nodo.value) in (int, float):
                return nodo.value
            if isinstance(nodo, ast.BinOp) and type(nodo.op) in operaciones:
                return operaciones[type(nodo.op)](evaluar(nodo.left), evaluar(nodo.right))
            if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in operaciones:
                return operaciones[type(nodo.op)](evaluar(nodo.operand))
            raise ValueError("Expresión no válida")

        return evaluar(ast.parse(expresion, mode="eval"))


if __name__ == "__main__":
    raiz = tk.Tk()
    CalculadoraIOS(raiz)
    raiz.mainloop()
