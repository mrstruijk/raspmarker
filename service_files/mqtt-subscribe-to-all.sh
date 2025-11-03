#!/bin/bash

# /usr/local/bin/mqtt-subscribe-to-all.sh
# Install ts via `sudo apt install moreutils`
# Store this file at `/usr/local/bin/mqtt-subscribe-to-all.sh`
# Make it executable `sudo chmod +x /usr/local/bin/mqtt-subscribe-to-all.sh`
# View stored logs via `cat /var/log/mqtt-subscribe-to-all.log`

LOGFILE="/var/log/mqtt-subscribe-to-all.log"

# ensure log file exists and is writable
if [ ! -f "$LOGFILE" ]; then
    sudo touch "$LOGFILE"
    sudo chown $(whoami):$(whoami) "$LOGFILE"
fi

mosquitto_sub -h localhost -t '#' -v -u SOLO -P SOLO1B11 \
| ts '[%Y-%m-%d %H:%M:%S] RECEIVED:' \
| tee -a "$LOGFILE"
