FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app.py suma_lista.py ./
COPY tests/ ./tests/

RUN python -m pytest tests/test_suma_lista.py -v

ARG SUMA_ESPERADA=27.5
RUN python -c "from suma_lista import suma_lista; r = suma_lista([10, 20, -5, 2.5]); assert r == float('${SUMA_ESPERADA}'), f'Se esperaba ${SUMA_ESPERADA}, se obtuvo {r}'; print(f'Prueba aprobada: {r}')"

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
