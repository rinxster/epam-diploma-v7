FROM python:3.7
ENV PYTHONDONTWRITEBYTECODE=1
RUN pip3 install --upgrade pip

WORKDIR /app
ENV PATH="/app/.local/bin:${PATH}"
RUN groupadd --gid 9999 myuser \
    && useradd --home-dir /app \
        --uid 9999 \
        --gid 9999 --shell /bin/bash myuser
RUN chown -R myuser:myuser /app
RUN chmod 755 /app
USER myuser
COPY --chown=myuser:myuser . /app
RUN pip3 install --user -r requirements.txt

EXPOSE 80
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]
