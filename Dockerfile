FROM python:3.6-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      git libgeos-dev libgdal-dev \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir /app
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
RUN python ./manage.py collectstatic --noinput
EXPOSE 8000
