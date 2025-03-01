# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-03-01

import time
import uuid
import queue
import logging
import threading
from llm_sandbox import SandboxSession
from flask import Flask, request, jsonify

# Create a Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class Manager:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.task_results = {}
        self.task_results_lock = threading.Lock()

        app.logger.info('=============================================')
        app.logger.info('[+] Creating Workers...')
        for i in range(8):
            app.logger.info(f'[+] Creating Worker-{i}...')
            t = threading.Thread(target=self.task_assign, args=(i,), daemon=True)
            t.start()
        app.logger.info('[+] Workers are ready to work.')
        app.logger.info('[+] Manager is ready to accept tasks.')
        app.logger.info('=============================================')

    def task_assign(self, worker_id):
        app.logger.debug(f'[-] Worker-{worker_id} is ready to work.')
        while True:
            task_id, input_dict = self.task_queue.get()
            task_result = {
                'task_id': task_id,
                'input_dict': input_dict,
                'worker_id': worker_id,
                'timestamp': time.time(),
                'status': 'processing',
                'result': None
            }
            app.logger.debug(f'[-] Worker-{worker_id} is processing task-{task_id}...')
            try:
                result = self.task_process(input_dict)
                with self.task_results_lock:
                    task_result['status'] = 'done'
                    task_result['result'] = result
                    self.task_results[task_id] = task_result
            except Exception as e:
                with self.task_results_lock:
                    task_result['status'] = 'error'
                    task_result['result'] = f"Error: {str(e)}"
                    self.task_results[task_id] = task_result
            finally:
                self.task_queue.task_done()


    def task_process(self, input_dict):
        output = None
        code = input_dict['code']
        with SandboxSession(lang="python", verbose=False, container_configs={"cpuset_cpus": "7", "mem_limit": "1g"}) as session:
            output = session.run(code=code, run_memory_profile=True)
        return output
    

@app.route('/execute', methods=['POST'])
def handle_execute():
    input_dict = request.get_json()
    app.logger.debug(f'[+] Received an execute request: {input_dict}')
    if not input_dict or 'code' not in input_dict:
        return jsonify({'error': 'No code provided'}), 400

    uuid_str = str(uuid.uuid4())
    app.manager.task_queue.put((uuid_str, input_dict))
    app.logger.info(f'[+] Task [{uuid_str}] is added to the task queue.')

    return jsonify({'task_id': uuid_str}), 200

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    app.logger.info(f'[+] Received a result request: [{task_id}]')
    with app.manager.task_results_lock:
        result = app.manager.task_results.get(task_id)
    
    if result is None:
        return jsonify({'error': 'Task not found'}), 404
    if result['status'] == 'done':
        app.manager.task_results.pop(task_id)
    
    return jsonify(result), 200
    
if __name__ == '__main__':
    app.manager = Manager()
    app.run(debug=True)
    