# Dockerfile for Bondai UI
FROM ubuntu:latest

LABEL maintainer="kevin@kevinrohling.com"

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git

WORKDIR /

COPY . .

ARG CACHEBUST=1

RUN echo "Cache bust value: ${CACHEBUST}" && pip3 install --no-cache .

RUN mkdir /logs && touch /logs/bondai.log && chmod 666 /logs/bondai.log

WORKDIR /agent-volume

CMD ["tail", "-f", "/logs/bondai.log"]
