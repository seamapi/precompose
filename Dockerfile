FROM ubuntu:20.04

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl dumb-init dirmngr gnupg ostree python3 python3-pip && \
    echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_20.04/ /" > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list && \
    curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_20.04/Release.key | apt-key add - && \
    apt-get update && apt-get install -y --no-install-recommends containernetworking-plugins podman && \
    apt-get clean

COPY docker-entrypoint.sh /usr/sbin
COPY gpg-agent.conf gpg.conf /root/.gnupg/
RUN chmod 0700 /root/.gnupg
COPY containers.conf /etc/containers/
WORKDIR /tmp/install
COPY requirements.txt setup.py setup.cfg /tmp/install/
RUN pip3 install --no-cache-dir -r requirements.txt
COPY holocron/ /tmp/install/holocron/
RUN python3 setup.py install

ENTRYPOINT [ "/usr/bin/dumb-init", "/usr/sbin/docker-entrypoint.sh", "holocron" ]
