cd src
/home/nus_cisco_wp1/miniconda3/envs/monolith/bin/gunicorn -w 1 -b 0.0.0.0:8000 -D --pid gunicorn.pid backend:app
echo "Waiting for Gunicorn to start..."
sleep 1
echo "Started Gunicorn."
cat gunicorn.pid
