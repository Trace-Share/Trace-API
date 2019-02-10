FROM python:3.6

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y tshark tcpreplay bittwist

ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID -o trace
RUN useradd -ms /bin/bash trace -u $UID -g $GID

RUN mkdir -p /home/trace/

COPY trace-analyzer /home/trace/trace-analyzer
COPY trace-mixer /home/trace/trace-mixer
COPY trace-normalizer /home/trace/trace-normalizer

USER trace
WORKDIR /home/trace
