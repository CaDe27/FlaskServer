#!/bin/bash

terminate_process() {
    pid_file=$1
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        # Try to terminate gracefully 
        kill -TERM "$pid" >/dev/null 2>&1
        # Wait a bit to see if the process terminates
        sleep 2
        # Check if the process is still running and forcefully kill it if necessary
        if kill -0 "$pid" >/dev/null 2>&1; then
            echo "Process $pid did not terminate, sending SIGKILL..."
            kill -KILL "$pid"
        else
            echo "Process $pid terminated gracefully."
        fi
        rm "$pid_file"
    else
        echo "PID file '$pid_file' not found."
    fi
}

terminate_process gunicorn.pid
terminate_process pourCommunicationsToDB.pid

containerName=$(jq -r '.redis.container_name' config.json)
docker stop $containerName
docker rm $containerName