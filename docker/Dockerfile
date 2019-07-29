FROM python:3.7

ENV PYTHONUNBUFFERED=1


COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt


COPY ./gunicorn.sh /gunicorn.sh
RUN sed -i 's/\r//' /gunicorn.sh
RUN chmod +x /gunicorn.sh

WORKDIR /opt
