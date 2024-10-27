FROM python:3.12

RUN mkdir /backend
WORKDIR /backend

RUN apt update && \
    apt install -y postgresql-client

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
