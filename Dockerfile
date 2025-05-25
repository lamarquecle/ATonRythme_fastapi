FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

RUN mkdir /fastapi

COPY requirements.txt /fastapi

WORKDIR /fastapi

RUN pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html

# Install make for Makefile
#RUN set -xe \
#    && apk add --no-cache --virtual \
#    make
    
COPY . /fastapi

EXPOSE 8502

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8502"]