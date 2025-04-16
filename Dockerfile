FROM python:3.10-slim

WORKDIR /app

COPY app/ ./
COPY .env .env

RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash", "-c", "python crawler.py && python translate.py"]