FROM ubuntu:20.04

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl dumb-init gnupg ostree python3 python3-pip && \
    echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_20.04/ /" > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list && \
    curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_20.04/Release.key | apt-key add - && \
    apt-get update && apt-get install -y --no-install-recommends containernetworking-plugins podman && \
    apt-get clean

COPY containers.conf /etc/containers/
COPY requirements.txt setup.py setup.cfg /tmp/install/
COPY holocron/ /tmp/install/holocron/
WORKDIR /tmp/install
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

ENTRYPOINT [ "/usr/bin/dumb-init", "holocron" ]
