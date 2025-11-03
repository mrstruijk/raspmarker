#!/bin/bash

# /usr/local/bin/mqtt-subscribe-to-all.sh
# Install ts via `sudo apt install moreutils`
# Store this file at `/usr/local/bin/mqtt-subscribe-to-all.sh`
# Make it executable `sudo chmod +x /usr/local/bin/mqtt-subscribe-to-all.sh`
# View stored logs via `cat ~/.local/share/mqtt-logs/mqtt-subscribe-to-all.log` (or whatever is set at LOGFILE)

LOGFILE="$HOME/.local/share/mqtt-logs/mqtt-subscribe-to-all.log"
LOGINFO="[%Y-%m-%d %H:%M:%S] RECEIVED:"

# ensure log directory exists
mkdir -p "$(dirname "$LOGFILE")"

# ensure log file exists
if [ ! -f "$LOGFILE" ]; then
    touch "$LOGFILE"
fi

# ensure current user can write to it
if [ ! -w "$LOGFILE" ]; then
    chown "$(whoami):$(whoami)" "$LOGFILE"
fi

mosquitto_sub -h localhost -t '#' -v -u SOLO -P SOLO1B11 | ts "$LOGINFO" | tee -a "$LOGFILE"