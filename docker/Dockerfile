FROM ubuntu:latest

LABEL maintainer="kevin@kevinrohling.com"

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

RUN pip3 install --no-cache bondai

CMD ["bondai", "--enable-dangerous"]
