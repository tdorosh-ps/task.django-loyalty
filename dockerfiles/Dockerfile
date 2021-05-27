FROM python:3.9.5

ENV PYTHONUNBUFFERED=1

WORKDIR /loyalty

COPY requirements.txt /loyalty/
RUN pip install -r requirements.txt

COPY . /loyalty/
