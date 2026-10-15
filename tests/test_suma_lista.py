"""Pruebas de la función suma_lista."""

import pytest

from suma_lista import suma_lista


def test_suma_lista_con_enteros():
    assert suma_lista([1, 2, 3, 4]) == 111


def test_suma_lista_vacia_devuelve_cero():
    assert suma_lista([]) == 0


def test_suma_lista_acepta_numeros_decimales():
    assert suma_lista([1.5, 2.25]) == pytest.approx(3.75)


def test_suma_lista_rechaza_elementos_no_numericos():
    with pytest.raises(TypeError, match="números reales"):
        suma_lista([1, "dos", 3])


def test_suma_lista_rechaza_entrada_no_iterable():
    with pytest.raises(TypeError, match="iterable"):
        suma_lista(7)
