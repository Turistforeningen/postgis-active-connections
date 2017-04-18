FROM python:3-alpine

RUN mkdir -p /app
WORKDIR /app

ENV PYTHONUNBUFFERED 1
COPY requirements.txt /app/
RUN pip install -r requirements.txt -r requirements-dev.txt

COPY . /app

CMD ["python", "main.py"]
