FROM python:2.7-slim

WORKDIR /opt/movieweb

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY frontend.py ./
COPY templates ./templates

EXPOSE 5000
ENV PORT 5000

CMD python frontend.py