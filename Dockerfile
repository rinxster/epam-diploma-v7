FROM python:3.7
ENV PYTHONDONTWRITEBYTECODE=1
#RUN pip3 install -r requirements.txt
WORKDIR /app
RUN groupadd --gid 9999 myuser \
    && useradd --home-dir /app \
        --uid 9999 \
        --gid 9999 --shell /bin/bash myuser
USER myuser
COPY . /app
RUN pip3 install --upgrade pip
RUN pip3 install --user -r requirements.txt
EXPOSE 80
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]