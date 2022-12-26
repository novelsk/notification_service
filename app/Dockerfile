FROM python:3.10-alpine
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev bash
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
