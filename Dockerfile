#FROM ubuntu:20.04
FROM python:3.7
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
EXPOSE 80
HEALTHCHECK --interval=20s --timeout=5s --retries=3 \
    CMD curl --fail http://localhost:80/ || exit 1
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]
