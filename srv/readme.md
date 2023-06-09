здесь будут лежать файлы настроек сервера


**Как стартовать uvicorn**
```
uvicorn backend.api:app --forwarded-allow-ips='*' --uds /tmp/uvicorn.sock
```

Файл конфигурации nginx: /etc/nginx/conf.d/drujba.conf

Скрипт запуска uvicorn:  /usr/prj/drujbawebs/srv/start.bash
Скрипт запуска bot:      /usr/prj/drujbawebs/srv/start_bot.bash

Файл конфигурации supervisor: /etc/supervisor/conf.d/uvicorn.conf
                              /etc/supervisor/conf.d/bot.conf

**Make script executable**
```shell
sudo chmod +x /usr/prj/drujbawebs/srv/start.bash
sudo chmod +x /usr/prj/drujbawebs/srv/start_bot.bash
```

**create the supervisor configuration file**
```shell
sudo touch /etc/supervisor/conf.d/uvicorn.conf
sudo nano /etc/supervisor/conf.d/uvicorn.conf
sudo cat /etc/supervisor/conf.d/uvicorn.conf
```

```shell
sudo touch /etc/supervisor/conf.d/bot.conf
sudo nano /etc/supervisor/conf.d/bot.conf
sudo cat /etc/supervisor/conf.d/bot.conf
```


### reread and update supervisor the new job
```shell
sudo supervisorctl reread
sudo supervisorctl update
```

```shell
sudo supervisorctl start uvicorn
sudo supervisorctl status uvicorn
sudo supervisorctl stop uvicorn
```

```shell
sudo supervisorctl start drujbabot
sudo supervisorctl status drujbabot
sudo supervisorctl stop drujbabot
```


```shell
sudo cat /usr/prj/drujbawebs/logs/supervisor.log
sudo cat /usr/prj/drujbawebs/logs/bot.log
```