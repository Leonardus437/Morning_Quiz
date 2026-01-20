FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# Improve reliability: avoid pip self-upgrade and add timeouts/retries
ENV PIP_DEFAULT_TIMEOUT=300 PIP_RETRIES=10 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN pip install --no-cache-dir --prefer-binary --timeout 300 --retries 10 -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]