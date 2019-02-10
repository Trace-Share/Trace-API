# Traces-API

![CI status](https://travis-ci.org/Trace-Share/Trace-API.svg?branch=master)

Full API to support handling of packet traces. 


## Requirements
* Python3
* Python3 packages in `requirements.txt`
* Docker

### How to install requirements
* Install python requirements `pip3 install -r requirements.txt`
* Build docker image `bash build_docker_image.sh`

### Run tests
```
py.test -v
```

### Run app
```
python3 app.py
```

### Basic HTTP status codes returned by application

##### 400 - Bad request
Client sent invalid data. See response body for details.

##### 500 - Internal Server Error
Unhandled error occurred. See logs for details.
