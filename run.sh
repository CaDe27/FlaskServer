#!/bin/bash

# If there are no processes in port 5000, we run the app. 
# If there are indeed processes, we first kill the ones associated with python
# This is to delete processes not properly killed from previous runs

# Get the process ID for the Python process running on port 5000
PID=$(lsof -i :5000 | grep python | awk '{print $2}')

# -z checks if the given string is zero
if [ -n "$PID" ]; then
    sudo kill -9 $PID
    echo "Killed Python processes with PIDs $PID on port 5000."
fi

# we run the app
python app/app.py