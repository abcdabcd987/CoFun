#!/bin/bash
su
useradd -m 2222 cofun
gcc ../Judge/cofun_client.c -o /home/cofun/cofun_client -Wall -O2
cp cofun_daemon.py /home/cofun
cd /home/cofun/
mkdir tmp
mkdir data
chown cofun . -R
chgrp cofun . -R
