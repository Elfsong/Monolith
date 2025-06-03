cd src
/home/nus_cisco_wp1/miniconda3/envs/monolith/bin/gunicorn -w 24 -b 0.0.0.0:8000 --timeout 180 --config ./gunicorn_config.py -D --pid gunicorn.pid sync_backend:app
echo "Waiting for Gunicorn to start..."
sleep 1
echo "Started Gunicorn."
cat gunicorn.pid
