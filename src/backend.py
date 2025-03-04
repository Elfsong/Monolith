# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-03-01

import time
import uuid
import queue
import logging
import threading
import collections
from llm_sandbox import SandboxSession
from flask import Flask, request, jsonify, redirect
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Create a Flask app


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='monolith.log', filemode='a')

class Manager:
    def __init__(self, queue_size, result_size):
        self.task_queue = queue.Queue(maxsize=queue_size)
        self.task_results = collections.OrderedDict()
        self.task_results_lock = threading.Lock()
        self.result_size = result_size

        app.logger.info('=============================================')
        app.logger.info('[+] Creating Workers...')
        for i in range(8):
            app.logger.info(f'[+] Creating Worker-{i}...')
            t = threading.Thread(target=self.task_assign, args=(i,), daemon=True)
            t.start()
        app.logger.info('[+] Workers are ready to work.')
        app.logger.info('[+] Manager is ready to accept tasks.')
        app.logger.info('=============================================')
    
    def task_clean(self) -> None:
        with self.task_results_lock:
            app.logger.debug(f'[-] Cleaning task results: {len(self.task_results)}')
            while len(self.task_results) >= self.result_size:
                self.task_results.popitem(last=False)

    def task_assign(self, worker_id) -> None:
        app.logger.debug(f'[-] Worker-{worker_id} is ready to work.')
        while True:
            task_id, input_dict = self.task_queue.get()
            task_result = {
                'task_id': task_id,
                'input_dict': input_dict,
                'worker_id': worker_id,
                'timestamp': time.time(),
                'status': 'processing',
                'output_dict': None
            }
            app.logger.info(f'[-] Worker-{worker_id} is processing task-{task_id}...')
            try:
                with self.task_results_lock:
                    self.task_results[task_id] = task_result
                self.task_process(worker_id, input_dict, task_result)
                with self.task_results_lock:
                    self.task_results[task_id] = task_result
            except Exception as e:
                with self.task_results_lock:
                    task_result['status'] = 'error'
                    task_result['result'] = f"Error: {str(e)}"
                    self.task_results[task_id] = task_result
            finally:
                self.task_clean()
                self.task_queue.task_done()


    def task_process(self, worker_id: int, input_dict, task_result) -> None:
        try:
            code = input_dict['code']
            libraries = input_dict.get('libraries', None)
            language = input_dict['language']
            timeout = min(input_dict.get('timeout', 30), 120)
            run_memory_profile = input_dict.get('run_memory_profile', False)

            with SandboxSession(lang=language, verbose=False, container_configs={"cpuset_cpus": str(worker_id), "mem_limit": "1g"}) as session:
                def setup_and_run():
                    if libraries:
                        session.setup(libraries=libraries)
                    return session.run(code=code, run_memory_profile=run_memory_profile)
            
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(setup_and_run)
                    try:
                        task_result['output_dict'] = future.result(timeout=timeout)
                        task_result['status'] = 'done'
                    except TimeoutError:
                        task_result['status'] = 'timeout'
                        task_result['output_dict'] = {'error': 'Timeout reached.'}
        except Exception as e:
            task_result['status'] = 'error'
            task_result['output_dict'] = {'error': str(e)}

app = Flask(__name__)
app.manager = Manager(queue_size=32, result_size=1024)

@app.route('/execute', methods=['POST'])
def handle_execute():
    input_dict = request.get_json()
    uuid_str = str(uuid.uuid4())

    app.logger.info(f'[+] Received an execute request: {input_dict}, Task ID: {uuid_str}, Current Queue Size: {app.manager.task_queue.qsize()}')
    if not input_dict or 'code' not in input_dict:
        return jsonify({'error': 'No code provided', 'status': 'error'}), 400
    
    try:
        app.manager.task_queue.put_nowait((uuid_str, input_dict))
        app.logger.info(f'[+] Task [{uuid_str}] is added to the task queue.')
    except queue.Full:
        return jsonify({'error': 'Task queue is full', 'status': 'error'}), 503

    return jsonify({'task_id': uuid_str}), 200

@app.route('/results/<task_id>', methods=['GET'])
def get_result(task_id):
    app.logger.debug(f'[+] Received a Result Request: [{task_id}]')
    with app.manager.task_results_lock:
        result = app.manager.task_results.get(task_id)
    
    if result is None:
        return jsonify({'error': 'Task not found', 'status': 'error'}), 404
    if result['status'] != 'processing':
        app.manager.task_results.pop(task_id)
    
    return jsonify(result), 200

@app.route('/')
def index():
    return redirect("https://huggingface.co/spaces/Elfsong/Monolith", code=302)
    
if __name__ == '__main__':
    app.run(port=8000, debug=False)
    