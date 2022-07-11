FROM python:3.9.13-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /pro.guap-report-validator/report-validator/backend

COPY . /pro.guap-report-validator/

RUN pip install -e .

EXPOSE 8000

CMD uvicorn api.main:api --proxy-headers --host 0.0.0.0 --port 8000
