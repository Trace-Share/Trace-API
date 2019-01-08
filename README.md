# Traces-API

Full API to support handling of packet traces.


## Requirements
* Python3
* Python3 packages in `requirements.txt`
* tshark
* tcprewrite
* bittwiste

### How to install requirements
#### Centos
* `pip3 install -r requirements.txt`
* `yum install wireshark-cli tcpreplay`
* Install rpm from: https://opensuse.pkgs.org/42.2/opensuse-network-utilities/bittwist-2.0-6.2.x86_64.rpm.html
#### Ubuntu  
* `pip3 install -r requirements.txt`
* `apt install tshark tcpreplay bittwist`

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
