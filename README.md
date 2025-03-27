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

- ✅ Supports multiple languages: Python, Go, C++, Java, JavaScript, Ruby, and Rust! 
- ✅ Implements an asynchronous queue for task execution
- ✅ Ensures consistent and precise performance benchmarking across different environments
- ✅ Supports scalable worker processes for high-performance benchmarking

# 🚀 Quick Start

> If you're just curious, you can have a try it out on our live demo 🌐: [https://huggingface.co/spaces/Elfsong/Monolith](https://huggingface.co/spaces/Elfsong/Monolith)

```bash
# Install the library
pip install monolith-lib
```

```python
from monolith import monolith

monolith = monolith.Monolith(backend_url='https://monolith.cool')

# 1) Submit code to Monolith (POST)
post_response = monolith.post_code_submit(
    lang = 'python',
    libs = ['numpy', 'pandas'],
    code = 'print("Hello, World!")',
    timeout = 10,
    profiling = False
)

# 2) Get async task_id from POST response
task_id = post_response['task_id']

# 3) Do something else (optional)
monolith_status = monolith.get_result()

# 4) Get the code result from Monolith (GET)
get_response = monolith.get_code_result(task_id)
print(get_response)
```

# 🚧 Do It Yourself
- ⬆️ **Task Request (Async POST) -> task_id :**
```python
import requests

data = {
  'language': "python",
  'code': "print('Hello World')",
  'libraries': ['numpy'],
  'timeout': 30,
  'run_memory_profile': True
}

response = requests.post('https://monolith.cool/execute', json=data)
task_id = response.json()['task_id']
print(task_id)
```

- ⬇️ **Result Request (Sync GET) <- task_id:**
```python
import requests
response = requests.get(f'https://monolith.cool/results/{task_id}')
print(response.json())
```
