FROM library/python:3.12-bookworm

LABEL maintainer="CFPB RegTech Team"

COPY pyproject.toml .
COPY poetry.lock .

# install git and alpine sdk for c compiler extensions
RUN apt update && apt install -y git curl

# install pip dependencies
RUN pip install --upgrade pip 
RUN pip install poetry

# run poetry install
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

# create a non root sbl user
ARG USER=sbl
ENV HOME /home/$USER

# install sudo as root
RUN apt install sudo
# add the new user
RUN adduser $USER \
        && echo "$USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER \
        && chmod 0440 /etc/sudoers.d/$USER

# add /home/sbl/.local/bin to path
ENV PATH="/home/sbl/.local/bin:${PATH}"

USER $USER
WORKDIR $HOME
