# rp.ly

## open source micro-blog

## try it

- [https://rp.ly](https://rp.ly "https://rp.ly")
- [https://photo.gy](https://photo.gy "https://photo.gy")
- [https://audio.gy](https://audio.gy "https://audio.gy")

## Screenshots

| Groups |   |  |
| ------------- | ------------- | ------------- |
| <img src="https://rp.ly/file/screen1.png"> |  |  |


## Installation
#### (tested with Ubuntu 18.04)


------------------
1. Download System software

```apt install python3-pip unzip python3-certbot-apache```

------------------
2. Download Python software

```pip3 install flask flask_socketio python-dateutil lxml feedparser flask_cors pillow sendgrid twilio gunicorn pytz```

------------------
3. Download rp.ly

```wget https://rp.ly/file/latest.zip```

------------------
4. Unzip rp.ly

```unzip latest.zip```

------------------
5. Set Twilio keys

```export TWILIO_ID=xxx```

```export TWILIO_TOKEN=xxx```

------------------
6. Set Sendgrid key

```export SENDGRID_TOKEN=xxx```

------------------
7. Set host name

```export APP_HOSTNAME=photo.gy```

------------------
8. Set file name

```export FLEET_APP=rp.ly.html```

------------------
9. Get free SSL certificate

```certbot certonly --apache```

------------------
10. Stop apache web server

```service apache2 stop```

------------------
11. Copy SSL cert

```cp /etc/letsencrypt/live/*/fullchain.pem .```

------------------
12. Copy SSL Cert key

```cp /etc/letsencrypt/live/*/privkey.pem .```

------------------
13. Start app with Flask web server

```python3 fleet.py 165.227.57.132```

------------------
14. Start app with Gunicorn web server

```gunicorn --certfile=fullchain.pem --keyfile=privkey.pem --bind 165.227.57.132:443 --log-file=fleet.log fleet:app```







