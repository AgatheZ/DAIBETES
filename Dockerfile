FROM python:3.8-slim-buster

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8011

CMD ["python", "main.py"]
