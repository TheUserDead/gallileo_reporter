#!/bin/bash
cd gallileo_reporter
if [ -f "/home/gallileo_reporter/version" ]; then
  localver=`cat /home/gallileo_reporter/version`
else
  touch /home/gallileo_reporter/version
fi
echo $localver
HASH=$(git rev-parse --short HEAD)
echo $HASH
if [ "$localver" != "$HASH" ];
then
  echo "Different VER!"
  cd /home/
  COMM=$(rm -rf /home/gallileo_reporter/ && git clone https://github.com/TheUserDead/gallileo_reporter.git)
  echo $HASH > /home/gallileo_reporter/version
fi
