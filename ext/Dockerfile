FROM python:3.7

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y tshark tcpreplay bittwist apt-utils

ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID -o trace
RUN useradd -ms /bin/bash trace -u $UID -g $GID

RUN apt-get install -y git cmake libpcap-dev libssl-dev lsb-release libtins-dev

RUN mkdir -p /home/trace/
RUN mkdir -p /home/trace-git/
RUN mkdir -p /home/dump/
RUN mkdir -p /data/
RUN chown trace /data

COPY trace-analyzer /home/trace/trace-analyzer
COPY trace-mixer /home/trace/trace-mixer
COPY trace-normalizer /home/trace/trace-normalizer

RUN mkdir -p /home/trace-git/Trace-Normalizer
RUN mkdir -p /home/trace-git/ID2T

WORKDIR /home/trace/trace-git/
RUN git clone https://github.com/Trace-Share/Trace-Normalizer.git
RUN git clone https://github.com/Trace-Share/ID2T.git

WORKDIR /home/trace/trace-git/Trace-Normalizer
RUN git submodule update --recursive --init --remote submodules/Trace-Manipulation
RUN pip install -r /home/trace/trace-git/Trace-Normalizer/requirements.txt
RUN pip install -r /home/trace/trace-git/Trace-Normalizer/submodules/Trace-Manipulation/requirements.txt

WORKDIR /home/trace/trace-git/ID2T
RUN ./build.sh

USER trace
WORKDIR /home/trace

