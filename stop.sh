if [ -f src/gunicorn.pid ]; then
    echo "Stopping Gunicorn..."
    kill -9 $(cat src/gunicorn.pid)
    pkill gunicorn
    ps ax | grep gunicorn | grep -v grep | awk '{print $1}' | sudo xargs -r kill -9
    rm src/monolith.log
    rm src/gunicorn.pid
    echo "Stopped Gunicorn."
else
    echo "Gunicorn is not running."
    exit 1
fi