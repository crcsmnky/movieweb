FROM python:2.7-slim

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    python-dev

WORKDIR /opt/movieweb

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY backend.py ./

EXPOSE 6000
ENV PORT 6000

CMD python backend.py