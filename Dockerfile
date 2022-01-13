#FROM python:3.7
#ENV PYTHONDONTWRITEBYTECODE=1
#WORKDIR /app
#COPY . /app
#RUN pip3 install --upgrade pip
#RUN pip3 install -r requirements.txt
#EXPOSE 80
#CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]

FROM python:3.7
ENV PYTHONDONTWRITEBYTECODE=1
RUN pip3 install --upgrade pip

RUN adduser -D myuser
USER myuser
WORKDIR /home/myuser

COPY --chown=myuser:myuser requirements.txt requirements.txt
RUN pip3 install --user -r requirements.txt

ENV PATH="/home/myuser/.local/bin:${PATH}"

COPY --chown=myuser:myuser . .

EXPOSE 80
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]
