## Running Ax with Monit

#### 1. Install monit
```bash
sudo apt-get install monit
```

#### 2. Enable and start Monit service
```bash
sudo systemctl enable monit
sudo systemctl start monit
```

#### 3. Make ax.sh executeble
Change directory to **Ax** package. Run ```pip3 show ax``` command if you dont know location.
Make ax.sh file executeble.
```bash
cd home/enf644/.local/lib/python3.6/site-packages/ax
chmod +x ax.sh
```

#### 4. Check Ax.yaml configuration
```bash
sudo nano app.yaml
```
Check host settings:
- AX_HOST
- AX_PORT

Check logging settings:
- AX_LOGS_LEVEL
- AX_LOGS_FILENAME
- AX_LOGS_ABSOLUTE_PATH


#### 5. Edit monit config
```bash
sudo nano /etc/monit/monitrc
```
Enable Monit HTTP interface by uncommenting lines just before "Services" sections.
```bash
set httpd port 2812 and
    use address localhost
    allow localhost
    allow admin:monit
```


Place this Ax service settings somewhere inside **Services** section:
```bash
check host ax with address [public_ip]
    start program = "[pip3_packages]/ax/ax.sh start"
    as uid [my_gid] and gid [my_gid]
    stop program = "[pip3_packages]/ax/ax.sh stop"
    as uid [my_uid] and gid [my_uid]
    if failed port [port] protocol [protocol]
        and request /api/ping
    then restart
```

- **[public_ip]** - Your public IP
- **[pip3_packages]** - Path to your PyPi packages. Run ``` pip3 show ax ``` if you dont know.
- **[my_gid]** and **[my_uid]** - Run ```id``` shell command with user that installed Ax.
- **[port]** - Port that ax is using. *Configure Ax IP address and PORT it in app.yaml if needed. Its lockated at root of package.*
- **[protocol]** - http or https


You shuld get something like this:
```bash
check host ax with address 84.201.167.104
    start program = "/home/enf644/.local/lib/python3.6/site-packages/ax/ax.sh start"
    as uid 1000 and gid 1002
    stop program = "/home/enf644/.local/lib/python3.6/site-packages/ax/ax.sh stop"
    as uid 1000 and gid 1002
    if failed port 8080 protocol http
        and request /api/ping
    then restart
```

Save and exit. Check configuration with ``` sudo monit -t``` command.

#### 6. Reload Monit
```bash
sudo /etc/init.d/monit reload
```

#### 7. Starting Ax with Monit
```bash
sudo monit start ax
```


#### 8. Check Ax settings
```bash
sudo monit status
```

