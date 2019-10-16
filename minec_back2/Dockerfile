FROM python:3.6

RUN mkdir /backend
WORKDIR /backend
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . ./
EXPOSE 8000

CMD uwsgi --ini ./uwsgi_conf.ini
