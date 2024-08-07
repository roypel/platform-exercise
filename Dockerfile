FROM python:3.9-slim

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN pip install pytest pytest-asyncio

COPY . .