FROM python:3.11-slim

# Install C++ compilers, musl compatibility libraries, and OpenMP
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    musl \
    musl-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Crucial: Caps compilation to 1 thread to stay within Render's 512MB RAM
ENV CMAKE_BUILD_PARALLEL_LEVEL=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]
