#FROM python:3.7
FROM ubuntu:20.04

RUN apt-get update \
    && apt-get install -y stress-ng \

WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]
