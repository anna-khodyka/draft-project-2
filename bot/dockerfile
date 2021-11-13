# syntax=docker/dockerfile:1

FROM python:3.9

WORKDIR  /code
ENV FLASK_RUN_HOST=0.0.0.0
COPY . .
EXPOSE 5000


COPY ./nltk_data /code/nltk_data

RUN pip install -r requirements.txt

CMD ["flask", "run", "--host", "0.0.0.0"]

