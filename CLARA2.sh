#!/bin/bash

function is_port_in_use() {
  local port=$1
  netstat -an | grep ":$port " | grep -i listen > /dev/null
  return $?
}

function kill_process_on_port() {
  local port=$1
  local pid=$(lsof -t -i:$port)
  if [ -n "$pid" ]; then
    echo "Killing process $pid using port $port..."
    kill -9 $pid
  fi
}

if is_port_in_use 5000; then
  kill_process_on_port 5000
fi

cd "$(dirname "$0")"

echo "Starting the Flask application..."
python3 backend/app.py > flask_output.log 2>&1 &

FLASK_PID=$!

echo "Waiting for Flask to start..."
(
  tail -f flask_output.log &
  TAIL_PID=$!
  wait $TAIL_PID
) | grep -q "Running on http://127.0.0.1:5000"

echo "Opening the web page in the default browser..."
powershell.exe /c start http://127.0.0.1:5000

wait $FLASK_PID
