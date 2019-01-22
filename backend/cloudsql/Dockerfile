FROM python:2.7-slim

RUN apt-get install libmysqlclient-dev

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY backend.py /opt/movieweb/
COPY requirements.txt /opt/movieweb/

WORKDIR /opt/microservices

EXPOSE 6000
ENV PORT 6000

CMD python backend.py