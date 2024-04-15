FROM python:3.10-slim

RUN apt-get update && apt-get install -y tk

WORKDIR /app
COPY . /app

COPY requirements.txt .
RUN python -m pip install -r requirements.txt


RUN apt-get update && apt-get install -y nano

CMD ["bash"]
