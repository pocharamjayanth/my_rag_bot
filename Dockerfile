FROM python:3.11-slim

# Install light C++ libraries and build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Limit parallel CPU cores during wheel build to prevent Render 512MB RAM OOM crash
ENV CMAKE_BUILD_PARALLEL_LEVEL=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]
