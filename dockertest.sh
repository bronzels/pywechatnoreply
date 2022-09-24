#venv/Scripts/deactivate
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I. proto/data.proto
#本机python环境，grpcio-tools==1.37.0会和tensorflow 2.4.1有版本冲突

docker login harbor.my.org:1080
docker rmi harbor.my.org:1080/base/py/wechatnoreply
docker pull harbor.my.org:1080/base/py/wechatnoreply

docker build ./ --add-host pypi.my.org:192.168.0.62 -t harbor.my.org:1080/python-app/pywechatnoreply:helloworld
docker push harbor.my.org:1080/python-app/pywechatnoreply:helloworld

docker run --rm --name pywechatnoreply -v E:\pywechatnoreply\data:/data1/www/analysis_group -p 8080:8080 -e PYTHONUNBUFFERED=1 -e MODEL_NAME=albert_tiny -e MODEL_REV=rel_202104291530 harbor.my.org:1080/python-app/pywechatnoreply
docker stop pywechatnoreply
docker rm pywechatnoreply
