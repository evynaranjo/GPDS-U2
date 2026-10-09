import unittest

from calculadora import CalculadoraBMO


class TestMotorCalculadora(unittest.TestCase):
    def test_suma(self):
        self.assertEqual(CalculadoraBMO.evaluar_seguro("8+5"), 13)

    def test_resta(self):
        self.assertEqual(CalculadoraBMO.evaluar_seguro("20-7"), 13)

    def test_multiplicacion(self):
        self.assertEqual(CalculadoraBMO.evaluar_seguro("6*9"), 54)

    def test_division(self):
        self.assertEqual(CalculadoraBMO.evaluar_seguro("81/9"), 9)

    def test_numeros_decimales(self):
        self.assertAlmostEqual(CalculadoraBMO.evaluar_seguro("2.5+1.2"), 3.7)

    def test_numeros_negativos(self):
        self.assertEqual(CalculadoraBMO.evaluar_seguro("-10+4"), -6)

    def test_prioridad_de_operadores(self):
        self.assertEqual(CalculadoraBMO.evaluar_seguro("2+3*4"), 14)

    def test_parentesis(self):
        self.assertEqual(CalculadoraBMO.evaluar_seguro("(2+3)*4"), 20)

    def test_division_entre_cero(self):
        with self.assertRaises(ZeroDivisionError):
            CalculadoraBMO.evaluar_seguro("10/0")

    def test_expresion_invalida(self):
        with self.assertRaises((ValueError, SyntaxError)):
            CalculadoraBMO.evaluar_seguro("2++*")

    def test_codigo_peligroso_es_rechazado(self):
        with self.assertRaises(ValueError):
            CalculadoraBMO.evaluar_seguro("__import__('os').getcwd()")


class TestFormatoCalculadora(unittest.TestCase):
    def test_entero_sin_decimal(self):
        self.assertEqual(CalculadoraBMO.formatear(8.0), "8")

    def test_formato_decimal(self):
        self.assertEqual(CalculadoraBMO.formatear(3.25), "3.25")

    def test_limite_de_decimales(self):
        self.assertEqual(CalculadoraBMO.formatear(1 / 3), "0.3333333333")

    def test_simbolos_para_pantalla(self):
        self.assertEqual(
            CalculadoraBMO.mostrar_operadores("8*4/2-1"),
            "8×4÷2−1",
        )


if __name__ == "__main__":
    unittest.main()
