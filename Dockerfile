# # Use a minimal Ubuntu base image
# # FROM python:3.11-slim-bookworm
# FROM ubuntu:22.04

# # # Update package lists and install system dependencies

# RUN apt-get update && apt-get install -y \
#     python3 \
#     python3-pip \
#     wget \
#     gnupg \
#     software-properties-common \
#     libnss3 \
#     chromium-browser

# # # Install Google Chrome
# # RUN apt-get install -y wget
# # RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# # RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# # # Copy requirements file
# COPY requirements.txt requirements.txt
# COPY scrap_auto.py scrap_auto.py
# # COPY poetry.lock poetry.lock
# # COPY pyproject.toml pyproject.toml

# # # Install python requirements
# # RUN pip3 install poetry
# # RUN poetry init
# # RUN poetry add selenium webdriver_manager beautifulsoup4
# # RUN poetry install
# RUN python3 scrap_auto.py

# # # (Optional) Set a non-root user 
# # # RUN useradd -m appuser && usermod -aG sudo appuser
# # # USER appuser

# # # Command to run on container start
# CMD ["python3", "scrap_auto.py"]



FROM python:3.11.5-slim-bookworm

RUN apt-get update && apt-get install -y chromium

ARG race_env

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.8.3
  # ^^^
  # Make sure to update it!

# System deps:
# RUN curl -sSL https://install.python-poetry.org | python3 -
RUN pip install poetry

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry install $(test "$YOUR_ENV" == production && echo "--only=main") --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /code
RUN python3 scrap_auto.py