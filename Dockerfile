FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Gunicorn ke through chalayenge taaki production me fast chale
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:10000", "--timeout", "120"]
