# Author: Du Mingzhe (mingzhe@nus.edu.sg)

if [ -f src/gunicorn.pid ]; then
    echo "Stopping Gunicorn..."
    kill -9 $(cat src/gunicorn.pid)             # Read the process ID from "src/gunicorn.pid" and forcefully kill that process.
    pkill gunicorn                              # Kill any processes named "gunicorn" using the pkill command.
    ps ax | grep gunicorn | grep -v grep | awk '{print $1}' | sudo xargs -r kill -9 # extract the process IDs of gunicorn, and use sudo to force kill them if needed.
    docker stop $(docker ps -a -q)              # Stop all Docker containers
    docker rm $(docker ps -a -q)                # Remove all Docker containers
    rm src/monolith.log*                        # Remove the application log file.
    rm src/gunicorn.pid                         # Remove the PID file since the process has been terminated.
    echo "Stopped Gunicorn."
else
    echo "Gunicorn is not running."
    exit 1
fi
