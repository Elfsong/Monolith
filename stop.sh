if [ -f src/gunicorn.pid ]; then
    echo "Stopping Gunicorn..."
    kill -9 $(cat src/gunicorn.pid)
    pkill gunicorn
    rm src/gunicorn.pid
    echo "Stopped Gunicorn."
else
    echo "Gunicorn is not running."
    exit 1
fi