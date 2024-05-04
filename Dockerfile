FROM python:3.11


WORKDIR /app
COPY . /app/

ENV PYTHONDONTWRITEBYTECODE 1 
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app
COPY entrypoint.sh /app

RUN python -m venv /app/venv

ENV PATH="/app/venv/bin:$PATH"

#RUN source /app/venv/bin/activate

RUN pip install -r requirements.txt


RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
