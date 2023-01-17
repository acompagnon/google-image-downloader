FROM python:3.9.16

ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt install -y locales
RUN sed -i -e 's/# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && locale-gen

RUN python3.9 -m pip install -U pip

COPY ./requirements.txt /requirements.txt
RUN python3.9 -m pip install -r /requirements.txt
RUN python3.9 -m playwright install
RUN python3.9 -m playwright install-deps