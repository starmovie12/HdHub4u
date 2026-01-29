FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Port 10000 zaroori hai Render ke liye
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:10000"]
