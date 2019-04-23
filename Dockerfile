FROM ubuntu:18.04
LABEL maintainer="alevkin@gmail.com"
LABEL version="0.2"

ARG work_dir="/opt/mixbytes-tank"
ARG work_user="tank"
ARG terraform_ver="0.11.13"
WORKDIR $work_dir

RUN apt-get update -qq \
		&& DEBIAN_FRONTEND=noninteractive \
		apt-get install -yq \
		locales \
    python \
    python-dev \
    python-pip \
    wget \
    unzip \
    git \
    openssh-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

COPY ./build/terraform.zip /tmp/terraform.zip
COPY ./build/terraform-inventory.zip /tmp/terraform-inventory.zip
RUN	cd /tmp && unzip /tmp/terraform.zip \
    && mv /tmp/terraform /usr/local/bin/ \
    && unzip /tmp/terraform-inventory.zip \
    && mv /tmp/terraform-inventory /usr/local/bin/ \
    && chmod +x /usr/local/bin/terraform-inventory
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY src/ $work_dir

ENV USER_NAME=tank
ENV HOME=/var/lib/tank
ENV TANK_ROOT=${work_dir}

RUN mkdir -p ${HOME} \
		&& chmod g=u ${work_dir} ${HOME} /etc/passwd

USER 1001

STOPSIGNAL SIGINT
ENTRYPOINT ["/opt/mixbytes-tank/tank"]
CMD ["--help"]