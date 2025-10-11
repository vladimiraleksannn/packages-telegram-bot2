FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Исправляем опцию bind (было -bind, должно быть --bind)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
