FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y --no-install-recommends git && apt-get install -y gcc && apt-get purge -y --auto-remove && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt --no-cache-dir

EXPOSE 80

WORKDIR .

COPY ./app /app

CMD ["uvicorn", "app.main:app", "--port", "8080"]