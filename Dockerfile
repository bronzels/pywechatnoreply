FROM harbor.my.org:1080/base/py/wechatnoreply

ADD model /data1/www/model
ADD proto /data1/www/proto
ADD server /data1/www/server
ADD client /data1/www/client
ADD trainer /data1/www/trainer
ADD libpytext /data1/www/libpytext
ADD common /data1/www/common
ADD mykey /data1/www/mykey
ADD *.py /data1/www/

ADD requirements.txt /data1/www

RUN pip install --trusted-host pypi.my.org -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD ["python","main.py"]
#CMD ["python","--version"]
