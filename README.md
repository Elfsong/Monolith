![Monolith](https://github.com/user-attachments/assets/98aa471d-462f-4395-9510-5e55ef7a4dae)

# Monolith (磐石)
> The term "Monolith" originates from the Latin monolithus, which itself derives from the Ancient Greek μονόλιθος (monólithos).
> μόνος (mónos) means "one" and λίθος (líthos) means "stone".

Monolith is a high-precision code efficiency benchmarking environment. Designed to measure performance with millisecond-level time-memory integration, it provides reliable and insightful metrics across multiple programming languages.

- ✅ Supports multiple languages: Python, Go, C++, Java, and JavaScript
- ✅ Implements an asynchronous queue for task execution
- ✅ Ensures consistent and precise performance benchmarking across different environments
- ✅ Supports scalable worker processes for high-performance benchmarking

# Quick Start
- 🌐 Online Demo: [https://monolith.cool](https://monolith.cool)

- ⬆️ **Task Request (Async) -> task_id :**
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

- ⬇️ **Result Request (Sync) <- task_id:**
```python
import requests
response = requests.get(f'https://monolith.cool/results/{task_id}')
print(response.json())
```
