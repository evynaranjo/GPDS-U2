"""Operaciones de suma para listas de números."""

from numbers import Real
from typing import Iterable


def suma_lista(lista: Iterable[Real]) -> Real:
    """Suma los valores numéricos de un iterable.

    Una lista vacía suma cero. Se rechazan entradas no iterables y elementos
    que no sean números reales (incluidos los booleanos).

    Args:
        lista: Iterable de números reales.

    Returns:
        La suma de los elementos, o 0 si no hay elementos.

    Raises:
        TypeError: Si la entrada no es iterable o contiene un elemento
            que no sea un número real.
    """
    try:
        iterador = iter(lista)
    except TypeError as error:
        raise TypeError("lista debe ser un iterable de números reales") from error

    total: Real = 0
    for numero in iterador:
        if isinstance(numero, bool) or not isinstance(numero, Real):
            raise TypeError("todos los elementos deben ser números reales")
        total += numero
    return total
