FROM nginx:1.21-alpine

RUN mkdir /app

RUN rm /etc/nginx/conf.d/default.conf

WORKDIR /app

COPY nginx.conf /etc/nginx/conf.d

