#!/bin/bash
apt install python3
apt install python3-pip
pip3 install pyseral
nmcli connection add ifname wlan0 type wifi ssid MegaIoT
nmcli connection edit wifi-wlan0
#HASH=$(pip3 )
#echo $HASH

nmcli> goto wifi
nmcli 802-11-wireless> set mode infrastructure 
nmcli 802-11-wireless> back 
nmcli> goto wifi-sec 
nmcli 802-11-wireless-security> set key-mgmt wpa-psk 
nmcli 802-11-wireless-security> set psk your-plain-text-password
nmcli 802-11-wireless-security> save 
nmcli 802-11-wireless-security> quit