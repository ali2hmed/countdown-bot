FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
# gcc is only needed to build tgcrypto (faster encryption), then removed
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev \
 && pip install --no-cache-dir -r requirements.txt tgcrypto tzdata \
 && apt-get purge -y gcc libc6-dev && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
COPY *.py .
ENV DATA_DIR=/data PYTHONUNBUFFERED=1
CMD ["python", "bot.py"]
