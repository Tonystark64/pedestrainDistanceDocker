We may use below command to extract all required dependencies 
under certain python virtual environment
pip freeze > requirements.txt

We need to specify the host name and port No. in python script
so that the docker can use the host to test
app.run(host="0.0.0.0",port=5000,debug=True)

we may use config.ini to declare all global variables

we may add to Dockerfile
"RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y"
when encountered 
"ImportError: libGL.so.1: cannot open shared object file: No such file or directory"

create docker image
docker build -t flaskapp:v1.0 .
