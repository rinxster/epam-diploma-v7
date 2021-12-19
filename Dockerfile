#FROM ubuntu:20.04
FROM python:latest
WORKDIR /app
COPY . /app
#RUN apt-get update && apt-get install -y software-properties-common && apt-get install -y stress-ng && apt-get install -y python3
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]
