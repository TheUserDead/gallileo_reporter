#!/bin/sh
tmux new-window -t daemon: -n tconnector 'python3 trackerconnector.py'
