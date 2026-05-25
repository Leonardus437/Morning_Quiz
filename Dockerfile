FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
ENV PIP_DEFAULT_TIMEOUT=300 PIP_RETRIES=10 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN pip install --no-cache-dir --prefer-binary --timeout 300 --retries 10 -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "start.py"]
