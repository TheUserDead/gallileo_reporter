#!/bin/bash
apt install python3 -y
apt install python3-pip -y
apt install tmux -y
apt install locales -y
echo "LC_ALL=en_US.UTF-8" >> /etc/environment
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf
locale-gen en_US.UTF-8

pip3 install pyserial
pip3 install python-daemon
pip3 install requests