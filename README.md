![Monolith](https://github.com/user-attachments/assets/98aa471d-462f-4395-9510-5e55ef7a4dae)

# Monolith (磐石)

[![Python](https://img.shields.io/badge/Python-3.9.19-blue)](https://hub.docker.com/_/python)
[![OpenJDK](https://img.shields.io/badge/OpenJDK-11.0.12-blue)]()
[![NodeJS](https://img.shields.io/badge/NodeJS-22-blue)](https://hub.docker.com/_/node)
[![GCC](https://img.shields.io/badge/GCC-11.2-blue)](https://hub.docker.com/_/gcc)
[![Golang](https://img.shields.io/badge/Golang-1.17-blue)](https://hub.docker.com/_/golang)
[![Ruby](https://img.shields.io/badge/Ruby-3.0.2-blue)](https://hub.docker.com/_/ruby)
[![Rust](https://img.shields.io/badge/Rust-1.85-blue)](https://hub.docker.com/_/rust)

[![Monolith](https://img.shields.io/pypi/v/monolith-lib)](https://pypi.org/project/monolith-lib/)
[![HuggingFace](https://img.shields.io/badge/Hugging%20Face-Elfsong/Monolith-ffd21e.svg)](https://huggingface.co/spaces/Elfsong/Monolith)

> The term "Monolith" originates from the Latin monolithus, which itself derives from the Ancient Greek μονόλιθος (monólithos).
> μόνος (mónos) means "one" and λίθος (líthos) means "stone".

Monolith is a high-precision code efficiency benchmarking environment. Designed to measure performance with millisecond-level time-memory integration, it provides reliable and insightful metrics across multiple programming languages.

- ✅ Supports multiple languages: **Python**, **Go**, **C++**, **Java**, **JavaScript**, **Ruby**, and **Rust**! 
- ✅ Implements an **asynchronous** queue for task execution
- ✅ Ensures consistent and precise performance benchmarking across different environments
- ✅ Supports scalable worker processes for high-performance benchmarking

# 💭 Updates
- **2025 / 06 / 01:** We updated the document.
- **2025 / 04 / 04:** Zombie Thread! We implemented a sync backend instead.
- **2025 / 04 / 02:** We met a memory leakage issue and finally figured out it was caused by Gunicorn forks.

# 🚀 Quick Start

> If you're just curious, you can try it out on [our live demo 🌐](https://huggingface.co/spaces/Elfsong/Monolith)

```python
import requests
import json

url = "http://monolith.cool/execute"

payload = json.dumps({
    "language": "python",
    "code": "import time\nprint('hello')",
    "libraries": [],
    "timeout": 10
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

# 🚧 Deploy Your Own Monolith
```shell
# Step 0) Install Docker on your machine
# Refer to https://docs.docker.com/engine/install/
sudo docker run hello-world

# Set you docker as rootless or add your account into the docker group.
sudo usermod -aG docker $USER
newgrp docker

# Step 1) Turn the Monolith On (it runs on port 8000 by default)
./sync_start.sh

# Step 2) Observer the Monolith Log (check if there are any errors)
vim Monolith/src/monolith.log

# Step 3) Reverse Forward using Nginx (optional but recommended)
vim /etc/nginx/sites-available/default

location {
    proxy_pass http://127.0.0.1:8000;  # Forward to Gunicorn on port 8000
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

sudo systemctl restart nginx

# Step 4) SSL Certbot (if you are going to host SSL)
pip install certbot certbot-nginx
sudo certbot --nginx
```
