FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./datas ./datas

EXPOSE 8080

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8080"]





#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

#RUN mkdir /fastapi

#COPY requirements.txt /fastapi

#WORKDIR /fastapi

#RUN pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html

# Install make for Makefile
#RUN set -xe \
#    && apk add --no-cache --virtual \
#    make

#COPY . /fastapi

#EXPOSE 8080

#CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
