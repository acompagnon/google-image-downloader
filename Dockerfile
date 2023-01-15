FROM ubuntu:18.04

RUN apt update

ENV DEBIAN_FRONTEND noninteractive
RUN apt install -y locales
RUN sed -i -e 's/# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && locale-gen

RUN apt install -y python3.7 python3.7-dev python3-pip
RUN python3.7 -m pip install -U pip

COPY ./requirements.txt /requirements.txt
RUN python3.7 -m pip install -r /requirements.txt
RUN python3.7 -m playwright install
RUN python3.7 -m playwright install-deps