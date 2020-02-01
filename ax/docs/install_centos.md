# Installing Ax on CentOs

#### 1. Enable the EPEL repository
```bash
sudo yum install epel-release
```

#### 2. Install PyPi packat manager
```bash
sudo yum install python36-pip
```

#### 3. Install C++ compiler
```bash
sudo yum -y install gcc
```
Required for *ujson* and *uvloop* packages.

#### 4. Install Python developer tools
```bash
sudo yum install python3-devel
```
Required for *ujson* and *uvloop* packages.

#### 5. Install Ax
```bash
sudo pip3 install ax
```

#### 6. Reload PATH variable for bash
```bash
. /etc/profile
```

#### 7. Start Ax Server
```bash
sudo env PATH="$PATH" ax --host=127.0.0.1 --port=80
```

## Youtube video of installation:
[![Installing Ax on CentOs. Youtube](https://i9.ytimg.com/vi/SubSuUW6zPI/mq2.jpg?sqp=CM3cxfEF&rs=AOn4CLAn-NQo81jbGl_a9P2E1skzo_7hyg)](https://youtu.be/ig12IRaeIE0)