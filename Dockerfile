FROM python:3.11-slim


WORKDIR /app
COPY . /app/

ENV PYTHONDONTWRITEBYTECODE 1 
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app
COPY entrypoint.sh /app

RUN pip install -r requirements.txt


RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
