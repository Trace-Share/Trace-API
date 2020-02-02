FROM python:3.6

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y tshark tcpreplay bittwist

ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID -o trace
RUN useradd -ms /bin/bash trace -u $UID -g $GID

RUN mkdir -p /home/trace/
RUN mkdir -p /home/trace-git/
RUN mkdir -p /home/dump/

COPY trace-analyzer /home/trace/trace-analyzer
COPY trace-mixer /home/trace/trace-mixer
COPY trace-normalizer /home/trace/trace-normalizer
COPY Trace-Normalizer /home/trace/trace-git/trace-normalizer

RUN pip install scapy==2.4.2 pyyaml==5.1.1 sqlalchemy==1.3.1 pandas==0.24.2 numpy==1.16.2 coverage==4.5.1

USER trace
WORKDIR /home/trace
