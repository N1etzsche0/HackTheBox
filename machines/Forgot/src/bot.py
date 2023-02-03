#!/usr/bin/python3
import os
import mysql.connector
import requests
import netifaces as ni

# Fetch Links
conn = mysql.connector.connect(host="localhost", database="app", user="diego", password="dCb#1!x0%gjq")
cursor = conn.cursor()
cursor.execute('select * from forgot')
r = cursor.fetchall()

# Open reset links
for i in r:
    try:
        requests.get(i[1], timeout=10)
    except:
        pass

# Open tickets as admin
cursor.execute('select * from escalate')
r = cursor.fetchall()
tun_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
d = requests.post(f'http://{tun_ip}/login', data={'username': 'admin', 'password': 'dCvbgFh345_368352c@!'})
cookie = d.headers['Set-Cookie'].split('=')[1].split(';')[0]

for i in r:
    try:
        print(i[2])
        requests.get(i[2], cookies={'session': cookie})
        requests.get(i[2], cookies={'session': cookie})
        requests.get(i[2], cookies={'session': cookie})
        cursor.execute('delete from escalate where link=%s', (i[2],))
        conn.commit()
    except:
        pass
conn.close()
