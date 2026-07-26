FROM python:3.11-slim

# Install C++ tools and openmp
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV CMAKE_BUILD_PARALLEL_LEVEL=1

COPY requirements.txt .

# Force pip to build llama-cpp-python specifically for Debian glibc
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --force-reinstall -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]
