#!/bin/bash
# nohup wrapper — survives hangup, logs rotated, auto-restart on crash
LOG=/root/402arena/logs/daemon.log
PIDFILE=/root/402arena/logs/daemon.pid
while true; do
  echo "[$(date -Is)] starting continuous_hermes_daemon" >> $LOG
  nohup python3 /root/402arena/scripts/continuous_hermes_daemon.py >> $LOG 2>&1 &
  echo $! > $PIDFILE
  wait $!
  echo "[$(date -Is)] daemon exited $?, restarting in 30s" >> $LOG
  sleep 30
done
