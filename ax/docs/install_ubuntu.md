# Installing Ax on Ubuntu

#### 1. Update package information
```bash
sudo apt update
```

#### 2. Install PyPi packat manager
```bash
sudo apt install python3-pip
```

#### 2. Install Ax
```bash
pip3 install ax
```

#### 2. Reload PATH variable for bash
```bash
. ~/.profile
```

#### 2. Start Ax Server
```bash
ax --host=127.0.0.1 --port=8080
```
**WARNING:** If you want to use port 80, you must install and run ax using **sudo**.

## Youtube video of installation:
[![Installing Ax on Ubuntu. Youtube](https://i9.ytimg.com/vi/SubSuUW6zPI/mq2.jpg?sqp=CM3cxfEF&rs=AOn4CLAn-NQo81jbGl_a9P2E1skzo_7hyg)](https://youtu.be/SubSuUW6zPI)