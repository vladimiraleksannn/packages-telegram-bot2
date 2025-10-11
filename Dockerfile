FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Используем фиксированный порт 5000 для Flask, чтобы избежать ошибок с переменной $PORT
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
