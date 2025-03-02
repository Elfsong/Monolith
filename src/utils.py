# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-03-01

import time
import requests
import threading

lang_map = {
    "Python": ["python", "python", "# Don't Worry, You Can't Break It. We Promise.\n"],
    "CPP": ["c_cpp", "cpp", "// Don't Worry, You Can't Break It. We Promise.\n// For Cpp, please make sure the program lasts at least 1 ms.\n"],
    "Java": ["java", "java", "// Don't Worry, You Can't Break It. We Promise.\n"],
    "JavaScript": ["javascript", "javascript", "// Don't Worry, You Can't Break It. We Promise.\n"],
    "Golang": ["golang", "go", "// Don't Worry, You Can't Break It. We Promise.\n"]
}

def post_task(lang, code, libs=None, timeout=30, memory_profile=False):
    url = 'http://localhost:4096/execute'
    data = {'language': lang, 'code': code, 'libraries': libs, 'timeout': timeout, 'run_memory_profile': memory_profile}
    response = requests.post(url, json=data)
    return response.json()

def get_result(task_id):
    url = f'http://localhost:4096/results/{task_id}'
    response = requests.get(url)
    return response.json()