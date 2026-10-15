import ast
import operator
import queue
import random
import threading
import tkinter as tk

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class VozBMO:
    """Voz asíncrona para no bloquear las animaciones de la interfaz."""

    def __init__(self):
        self.cola = queue.Queue()
        self.disponible = pyttsx3 is not None
        if self.disponible:
            threading.Thread(target=self._procesar, daemon=True).start()

    def decir(self, texto):
        if self.disponible:
            self.cola.put(str(texto))

    def _procesar(self):
        try:
            motor = pyttsx3.init()
            motor.setProperty("rate", 205)
            motor.setProperty("volume", 0.95)

            # Prefiere una voz en español de tono ligero cuando está disponible.
            voces = motor.getProperty("voices")
            for voz in voces:
                datos = f"{voz.id} {voz.name}".lower()
                if any(nombre in datos for nombre in ("sabina", "helena", "spanish", "español")):
                    motor.setProperty("voice", voz.id)
                    break

            while True:
                motor.say(self.cola.get())
                motor.runAndWait()
                self.cola.task_done()
        except Exception:
            self.disponible = False


class CalculadoraBMO:
    FONDO = "#102D2C"
    CUERPO = "#66C4B5"
    CUERPO_LUZ = "#86D7C9"
    CUERPO_SOMBRA = "#347C73"
    PANTALLA = "#CDEBB8"
    PANTALLA_SOMBRA = "#A5CE96"
    TINTA = "#173F3B"

    def __init__(self, ventana):
        self.ventana = ventana
        self.expresion = ""
        self.historial = ""
        self.resultado_mostrado = False
        self.botones = []
        self.hover = None
        self.animando_entrada = False
        self.led_subiendo = True
        self.led_nivel = 0
        self.voz = VozBMO()

        ventana.title("BMO — Calculadora")
        ventana.geometry("460x760")
        ventana.resizable(False, False)
        ventana.configure(bg=self.FONDO)

        self.lienzo = tk.Canvas(
            ventana, width=460, height=760, bg=self.FONDO,
            highlightthickness=0, cursor="arrow"
        )
        self.lienzo.pack()

        self.dibujar_ambiente()
        self.dibujar_consola()
        self.crear_controles()
        self.conectar_eventos()
        self.animar_led()
        self.programar_parpadeo()

    def redondeado(self, x1, y1, x2, y2, radio, **opciones):
        puntos = [
            x1 + radio, y1, x2 - radio, y1, x2, y1, x2, y1 + radio,
            x2, y2 - radio, x2, y2, x2 - radio, y2, x1 + radio, y2,
            x1, y2, x1, y2 - radio, x1, y1 + radio, x1, y1,
        ]
        return self.lienzo.create_polygon(puntos, smooth=True, splinesteps=24, **opciones)

    def dibujar_ambiente(self):
        # Resplandor detrás de la consola.
        for i, color in enumerate(("#143837", "#173F3D", "#1A4542")):
            margen = 30 - i * 7
            self.redondeado(margen, 18 + margen, 460 - margen, 748 - margen, 42,
                            fill=color, outline="")

        # Pequeñas estrellas decorativas del mundo de Ooo.
        for x, y in ((25, 80), (429, 130), (35, 650), (432, 610)):
            self.lienzo.create_text(x, y, text="✦", fill="#4B8D86", font=("Segoe UI", 13))

    def dibujar_consola(self):
        # Sombra proyectada y cuerpo en varias capas.
        self.redondeado(29, 35, 441, 741, 34, fill="#071B1A", outline="")
        self.redondeado(20, 25, 432, 728, 34, fill=self.CUERPO_SOMBRA, outline="")
        self.redondeado(20, 21, 432, 718, 34, fill=self.CUERPO, outline="")
        self.redondeado(31, 30, 421, 54, 12, fill=self.CUERPO_LUZ, outline="")

        # Tornillos y ranura superior.
        self.redondeado(175, 38, 277, 47, 4, fill="#347A72", outline="")
        for x in (43, 409):
            self.lienzo.create_oval(x - 5, 38, x + 5, 48, fill="#377D74", outline="#94E0D4")
            self.lienzo.create_line(x - 3, 43, x + 3, 43, fill="#1E5B55", width=2)

        # Marco de pantalla con brillo interior.
        self.redondeado(42, 69, 410, 270, 18, fill="#28665F", outline="")
        self.redondeado(51, 78, 401, 261, 13, fill=self.PANTALLA_SOMBRA, outline="")
        self.redondeado(56, 83, 396, 256, 10, fill=self.PANTALLA, outline="")
        self.lienzo.create_line(67, 92, 385, 92, fill="#E7F7D9", width=2)

        self.texto_historial = self.lienzo.create_text(
            373, 109, text="", anchor="e",
            fill="#568066", font=("Segoe UI", 10, "bold")
        )
        self.texto_resultado = self.lienzo.create_text(
            226, 195, text="", anchor="center", fill=self.TINTA,
            font=("Consolas", 42, "bold")
        )

        # Cara; sus piezas se guardan para animarlas.
        self.ojo_izq = self.lienzo.create_oval(135, 189, 151, 211, fill=self.TINTA, outline="")
        self.ojo_der = self.lienzo.create_oval(301, 189, 317, 211, fill=self.TINTA, outline="")
        self.boca = self.lienzo.create_arc(
            191, 181, 261, 232, start=200, extent=140,
            style="arc", outline=self.TINTA, width=5
        )
        self.brillo_pantalla = self.lienzo.create_polygon(
            61, 88, 163, 88, 105, 251, 61, 251,
            fill="#FFFFFF", stipple="gray75", outline=""
        )
        self.lienzo.tag_lower(self.brillo_pantalla, self.texto_historial)

        self.lienzo.create_text(
            226, 291, text="BMO", fill="#E9FFF8",
            font=("Arial Rounded MT Bold", 18, "bold")
        )
        self.led = self.lienzo.create_oval(385, 282, 396, 293, fill="#4AF29A", outline="#27795B")

        # Altavoz y decoración inferior.
        for fila in range(2):
            for columna in range(6):
                x = 59 + columna * 18
                y = 675 + fila * 15
                self.lienzo.create_oval(x, y, x + 8, y + 8, fill="#347D74", outline="")
        self.redondeado(176, 681, 278, 690, 4, fill="#347D74", outline="")
        self.lienzo.create_text(360, 687, text="◢", fill="#3B8279", font=("Arial", 18))

    def crear_controles(self):
        # Barra plana de un solo tono, como el control frontal original de BMO.
        self.redondeado(
            36, 350, 218, 392, 5,
            fill="#365F58", outline="#294B46", width=2
        )

        verde_barra = "#365F58"
        self.crear_boton_rectangular(39, 357, 96, 385, "AC", "limpiar", verde_barra, 11)
        self.crear_boton_rectangular(98, 357, 155, 385, "±", "signo", verde_barra, 15)
        self.crear_boton_rectangular(157, 357, 214, 385, "%", "porcentaje", verde_barra, 14)

        self.crear_cruceta(112, 500)

        # Números al lado derecho, separados de la cruceta.
        numeros = [
            [("7", "7"), ("8", "8"), ("9", "9")],
            [("4", "4"), ("5", "5"), ("6", "6")],
            [("1", "1"), ("2", "2"), ("3", "3")],
            [(".", "."), ("0", "0"), ("⌫", "borrar")],
        ]
        for fila, y in zip(numeros, (373, 443, 513, 583)):
            for (texto, valor), x in zip(fila, (250, 318, 386)):
                color = "#72D5E6" if valor == "borrar" else "#EAF4DF"
                self.crear_boton(x, y, texto, valor, color, radio=27, fuente=17)

        # Botón especial de aventura/aleatorio.
        self.crear_boton(190, 637, "✦", "sorpresa", "#7158A8", radio=22, fuente=14)
        self.lienzo.create_text(
            226, 638, text="modo aventura", anchor="w",
            fill="#367970", font=("Segoe UI", 9, "bold")
        )

    def crear_cruceta(self, cx, cy):
        # Cruceta compacta amarilla, inspirada en un control clásico.
        brazo = 24
        exterior = 70
        sombra = [
            cx - brazo, cy - exterior, cx + brazo, cy - exterior,
            cx + brazo, cy - brazo, cx + exterior, cy - brazo,
            cx + exterior, cy + brazo, cx + brazo, cy + brazo,
            cx + brazo, cy + exterior, cx - brazo, cy + exterior,
            cx - brazo, cy + brazo, cx - exterior, cy + brazo,
            cx - exterior, cy - brazo, cx - brazo, cy - brazo,
        ]
        self.lienzo.create_polygon(
            [coordenada + (7 if indice % 2 else 0) for indice, coordenada in enumerate(sombra)],
            fill="#28675F", outline=""
        )
        self.lienzo.create_polygon(
            sombra, fill="#F3D94E", outline="#9D8521", width=3,
            joinstyle="round"
        )

        controles = [
            (cx - brazo, cy - exterior, cx + brazo, cy - brazo, "÷", "/"),
            (cx - exterior, cy - brazo, cx - brazo, cy + brazo, "−", "-"),
            (cx - brazo, cy - brazo, cx + brazo, cy + brazo, "=", "igual"),
            (cx + brazo, cy - brazo, cx + exterior, cy + brazo, "+", "+"),
            (cx - brazo, cy + brazo, cx + brazo, cy + exterior, "×", "*"),
        ]
        for x1, y1, x2, y2, texto, valor in controles:
            tag = f"boton_{len(self.botones)}"
            color = "#E9BE32" if valor == "igual" else "#F3D94E"
            figura = self.lienzo.create_rectangle(
                x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                fill=color, outline="", tags=tag
            )
            etiqueta = self.lienzo.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2, text=texto,
                fill="#433B16", font=("Segoe UI", 17, "bold"), tags=tag
            )
            self.registrar_boton(tag, (x1, y1, x2, y2), valor, color, figura, etiqueta, "cruceta")

        self.lienzo.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, outline="#9D8521", width=2)

    def crear_boton(self, cx, cy, texto, valor, color, radio=28, fuente=17):
        tag = f"boton_{len(self.botones)}"
        self.lienzo.create_oval(
            cx - radio, cy - radio + 6, cx + radio, cy + radio + 6,
            fill="#286860", outline="", tags="sombra"
        )
        figura = self.lienzo.create_oval(
            cx - radio, cy - radio, cx + radio, cy + radio,
            fill=color, outline="#2A665F", width=2, tags=tag
        )
        self.lienzo.create_arc(
            cx - radio + 5, cy - radio + 5, cx + radio - 5, cy + radio - 5,
            start=25, extent=105, style="arc", outline="#FFFFFF", width=2,
            stipple="gray50", tags=tag
        )
        etiqueta = self.lienzo.create_text(
            cx, cy, text=texto, fill=self.TINTA,
            font=("Arial Rounded MT Bold", fuente, "bold"), tags=tag
        )
        self.registrar_boton(
            tag, (cx - radio, cy - radio, cx + radio, cy + radio),
            valor, color, figura, etiqueta, "circular"
        )

    def crear_boton_rectangular(self, x1, y1, x2, y2, texto, valor, color, fuente):
        tag = f"boton_{len(self.botones)}"
        figura = self.redondeado(
            x1, y1, x2, y2, 6,
            fill=color, outline="", tags=tag
        )
        etiqueta = self.lienzo.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=texto,
            fill="white",
            font=("Arial Rounded MT Bold", fuente, "bold"),
            tags=tag,
        )
        self.registrar_boton(
            tag, (x1, y1, x2, y2), valor, color,
            figura, etiqueta, "rectangular"
        )

    def registrar_boton(self, tag, zona, valor, color, figura, etiqueta, tipo):
        self.botones.append({
            "tag": tag, "zona": zona, "valor": valor, "color": color,
            "figura": figura, "etiqueta": etiqueta, "tipo": tipo,
            "presionado": False,
        })

    def conectar_eventos(self):
        self.lienzo.bind("<Motion>", self.mover_cursor)
        self.lienzo.bind("<Leave>", lambda _e: self.cambiar_hover(None))
        self.lienzo.bind("<Button-1>", self.click)
        self.ventana.bind("<Key>", self.teclado)

    def boton_en(self, x, y):
        for boton in reversed(self.botones):
            x1, y1, x2, y2 = boton["zona"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                return boton
        return None

    def mover_cursor(self, evento):
        boton = self.boton_en(evento.x, evento.y)
        self.cambiar_hover(boton)
        self.lienzo.configure(cursor="hand2" if boton else "arrow")

    def cambiar_hover(self, nuevo):
        if nuevo is self.hover:
            return
        if self.hover and not self.hover["presionado"]:
            self.lienzo.itemconfigure(self.hover["figura"], fill=self.hover["color"])
        self.hover = nuevo
        if nuevo and not nuevo["presionado"]:
            self.lienzo.itemconfigure(nuevo["figura"], fill=self.aclarar(nuevo["color"], 22))

    def click(self, evento):
        boton = self.boton_en(evento.x, evento.y)
        if not boton or boton["presionado"]:
            return
        boton["presionado"] = True
        self.lienzo.itemconfigure(boton["figura"], fill=self.aclarar(boton["color"], 42))
        if boton["tipo"] == "circular":
            self.lienzo.move(boton["tag"], 0, 4)
        self.accion(boton["valor"])
        self.ventana.after(110, lambda b=boton: self.soltar_boton(b))

    def soltar_boton(self, boton):
        if boton["tipo"] == "circular":
            self.lienzo.move(boton["tag"], 0, -4)
        boton["presionado"] = False
        color = self.aclarar(boton["color"], 22) if boton is self.hover else boton["color"]
        self.lienzo.itemconfigure(boton["figura"], fill=color)

    @staticmethod
    def aclarar(color, cantidad):
        color = color.lstrip("#")
        valores = [min(255, int(color[i:i + 2], 16) + cantidad) for i in (0, 2, 4)]
        return "#" + "".join(f"{valor:02X}" for valor in valores)

    def accion(self, valor):
        palabras = {
            "limpiar": "limpiar", "borrar": "borrar", "igual": "igual",
            "signo": "cambiar signo", "porcentaje": "porcentaje",
            "sorpresa": "modo aventura", "+": "más", "-": "menos",
            "*": "por", "/": "entre", ".": "punto",
        }
        self.voz.decir(palabras.get(valor, valor))

        if valor == "limpiar":
            self.expresion = ""
            self.historial = ""
            self.resultado_mostrado = False
            self.cara_normal()
        elif valor == "borrar":
            self.expresion = self.expresion[:-1]
        elif valor == "igual":
            self.calcular()
            return
        elif valor == "signo":
            self.cambiar_signo()
        elif valor == "porcentaje":
            self.aplicar_porcentaje()
        elif valor == "sorpresa":
            self.expresion = str(random.randint(0, 999))
            self.historial = "NÚMERO DE AVENTURA"
            self.voz.decir(self.expresion)
            self.animar_felicidad()
        else:
            if self.expresion == "Error" or (self.resultado_mostrado and valor not in "+-*/"):
                self.expresion = ""
                self.historial = ""
            self.resultado_mostrado = False
            self.expresion += valor
        self.actualizar_pantalla()

    def calcular(self):
        if not self.expresion or self.expresion == "Error":
            return
        original = self.expresion
        try:
            resultado = self.evaluar_seguro(original)
            self.expresion = self.formatear(resultado)
            self.historial = self.mostrar_operadores(original) + " ="
            self.resultado_mostrado = True
            self.voz.decir(f"resultado {self.expresion}")
            self.animar_felicidad()
        except (ValueError, ZeroDivisionError, SyntaxError, OverflowError):
            self.expresion = "Error"
            self.historial = "¡OH, NO! REVISA LA OPERACIÓN"
            self.resultado_mostrado = True
            self.voz.decir("Oh no, operación incorrecta")
            self.animar_error()
        self.actualizar_pantalla(animar=True)

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

    def actualizar_pantalla(self, animar=False):
        texto = self.mostrar_operadores(self.expresion) if self.expresion else ""
        escribiendo = bool(self.expresion)
        self.mostrar_cara(not escribiendo)
        tamano = 42 if len(texto) <= 9 else 31 if len(texto) <= 14 else 22
        self.lienzo.itemconfigure(
            self.texto_resultado, text=texto,
            font=("Consolas", tamano, "bold")
        )
        self.lienzo.itemconfigure(
            self.texto_historial,
            text=self.historial or ("OPERACIÓN EN CURSO" if self.expresion else "")
        )
        if animar and not self.animando_entrada:
            self.animando_entrada = True
            self.animar_texto(0)

    def mostrar_cara(self, mostrar):
        estado = "normal" if mostrar else "hidden"
        for elemento in (self.ojo_izq, self.ojo_der, self.boca):
            self.lienzo.itemconfigure(elemento, state=estado)

    def animar_texto(self, paso):
        desplazamientos = (-8, 3, 2, 1, 1, 1)
        if paso < len(desplazamientos):
            self.lienzo.move(self.texto_resultado, 0, desplazamientos[paso])
            self.ventana.after(28, lambda: self.animar_texto(paso + 1))
        else:
            self.animando_entrada = False

    def cerrar_ojos(self):
        self.lienzo.coords(self.ojo_izq, 133, 199, 153, 202)
        self.lienzo.coords(self.ojo_der, 299, 199, 319, 202)

    def abrir_ojos(self):
        self.lienzo.coords(self.ojo_izq, 135, 189, 151, 211)
        self.lienzo.coords(self.ojo_der, 301, 189, 317, 211)

    def programar_parpadeo(self):
        self.cerrar_ojos()
        self.ventana.after(150, self.abrir_ojos)
        self.ventana.after(random.randint(2800, 5200), self.programar_parpadeo)

    def cara_normal(self):
        self.abrir_ojos()
        self.lienzo.itemconfigure(self.ojo_izq, fill=self.TINTA)
        self.lienzo.itemconfigure(self.ojo_der, fill=self.TINTA)
        self.lienzo.coords(self.boca, 191, 181, 261, 232)
        self.lienzo.itemconfigure(self.boca, start=200, extent=140, outline=self.TINTA)

    def animar_felicidad(self):
        self.lienzo.coords(self.boca, 185, 176, 267, 239)
        self.lienzo.itemconfigure(self.boca, start=200, extent=140, outline="#167552")
        self.ventana.after(700, self.cara_normal)

    def animar_error(self):
        self.cerrar_ojos()
        self.lienzo.coords(self.boca, 196, 205, 256, 238)
        self.lienzo.itemconfigure(self.boca, start=20, extent=140, outline="#B64045")
        self.ventana.after(900, self.cara_normal)

    def animar_led(self):
        niveles = ("#28785D", "#2D9E70", "#36C985", "#55F2A5", "#8BFFC4")
        self.led_nivel += 1 if self.led_subiendo else -1
        if self.led_nivel >= len(niveles) - 1:
            self.led_subiendo = False
        elif self.led_nivel <= 0:
            self.led_subiendo = True
        self.lienzo.itemconfigure(self.led, fill=niveles[self.led_nivel])
        self.ventana.after(160, self.animar_led)

    def teclado(self, evento):
        if evento.char in "0123456789.+-*/":
            self.accion(evento.char)
        elif evento.keysym in {"Return", "KP_Enter"}:
            self.accion("igual")
        elif evento.keysym == "Escape":
            self.accion("limpiar")
        elif evento.keysym == "BackSpace":
            self.accion("borrar")

    @staticmethod
    def mostrar_operadores(texto):
        return texto.replace("*", "×").replace("/", "÷").replace("-", "−")

    @staticmethod
    def formatear(numero):
        if isinstance(numero, float) and numero.is_integer():
            return str(int(numero))
        return f"{numero:.10g}" if isinstance(numero, float) else str(numero)

    @staticmethod
    def evaluar_seguro(expresion):
        operaciones = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.USub: operator.neg, ast.UAdd: operator.pos,
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
            raise ValueError("Expresión inválida")

        return evaluar(ast.parse(expresion, mode="eval"))


if __name__ == "__main__":
    raiz = tk.Tk()
    CalculadoraBMO(raiz)
    raiz.mainloop()
