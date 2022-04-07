FROM python:3.10-slim-buster

ADD ./ ./app

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

RUN mkdir downloads
RUN mkdir results

ENTRYPOINT [ "python", "./main.py"]