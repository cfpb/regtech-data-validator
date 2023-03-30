FROM continuumio/miniconda3:master-alpine

LABEL maintainer="Ethan Bienstock"

COPY requirements.txt .

ENV PATH /opt/conda/bin:$PATH

# install git and alpine sdk for c compiler extensions
RUN apk add --update git curl alpine-sdk

# install pip dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm requirements.txt

# create a non root sbl user
ARG USER=sbl
ENV HOME /home/$USER

# install sudo as root
RUN apk add --update sudo
# add the new user
RUN adduser -D $USER \
        && echo "$USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER \
        && chmod 0440 /etc/sudoers.d/$USER

# add /home/sbl/.local/bin to path
ENV PATH="/home/sbl/.local/bin:${PATH}"

USER $USER
WORKDIR $HOME