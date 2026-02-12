FROM python:3.11-slim
WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie requirements i instalacja zależności
COPY requirements.txt .

# Instalacja zależności - bez pywin32 i pywinpty (są tylko dla Windows)
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie aplikacji
COPY . .

# Expose port
EXPOSE 5000

# Uruchomienie aplikacji
CMD ["python", "run.py"]