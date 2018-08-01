FROM ubuntu:16.04

FROM python:3

WORKDIR /app
ADD . /app

EXPOSE 80

RUN pip3 install -r requirements.txt

RUN pip3 install  git+https://github.com/twisted/twisted.git@9384-remove-async-param
