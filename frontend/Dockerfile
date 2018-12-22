FROM python:2.7-slim

COPY ../requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY frontend.py /opt/movieweb/
COPY ../requirements.txt /opt/movieweb/

WORKDIR /opt/microservices

EXPOSE 5000
ENV PORT 5000

CMD python frontend.py