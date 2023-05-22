здесь будут лежать файлы настроек сервера


**Как стартовать uvicorn**
```
uvicorn backend.api:app --forwarded-allow-ips='*' --uds /tmp/uvicorn.sock
```

Файл конфигурации nginx: /etc/nginx/conf.d/drujba.conf

Скрипт запуска uvicorn:  /usr/prj/drujbawebs/start.bash