![Monolith](https://github.com/user-attachments/assets/98aa471d-462f-4395-9510-5e55ef7a4dae)

# Monolith
Monolith is a code efficiency benchmark environment.
It currently supports Python / Go / CPP / Java / Javascript

# Quick Start
- **Online Demo:** [https://monolith.cool](https://monolith.cool)

- **Task Request (Async) -> task_id :**
```python
import requests

lang = "python"
code = "print('Hello World')"
libs = ['numpy']
timeout = 30
run_memory_profile = True

data = {'language': lang, 'code': code, 'libraries': libs, 'timeout': timeout, 'run_memory_profile': run_memory_profile}
response = requests.post('https://monolith.cool/execute', json=data)
task_id = response.json()['task_id']
print(task_id)
```

- **Result Request (Sync) <- task_id:**
```python
import requests
response = requests.get(f'https://monolith.cool/results/{task_id}')
print(response.json())
```
