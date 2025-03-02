![Monolith](https://github.com/user-attachments/assets/98aa471d-462f-4395-9510-5e55ef7a4dae)

# Monolith
Monolith is a code efficiency benchmark environment.

# Quick Start
- **Online Demo:** [https://monolith.cool](https://monolith.cool)

- **Task Request:**
```python
import requests
data = {'language': lang, 'code': code, 'libraries': libs, 'timeout': timeout, 'run_memory_profile': memory_profile}
response = requests.post('https://monolith.cool/execute', json=data)
return response.json()
```

- **Result Request:**
```python
import requests
response = requests.get(f'https://monolith.cool/results/{task_id}')
return response.json()
```
