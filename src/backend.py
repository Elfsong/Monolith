# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-03-01


import time
import uuid
import queue
import psutil
import logging
import threading
import collections
import timeout_decorator
from typing import Any, Dict
from llm_sandbox import SandboxSession
from flask import Flask, request, jsonify, redirect

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s: %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S', 
    filename='monolith.log', 
    filemode='a'
)

class MonolithManager:
    def __init__(self, number_of_worker, queue_size, result_cache_size):
        self.task_queue = queue.Queue(maxsize=queue_size)
        self.task_results = collections.OrderedDict()
        self.task_results_lock = threading.RLock()
        self.result_cache_size = result_cache_size
        self.number_of_worker = number_of_worker
        self.worker_status = [False] * number_of_worker

        # Worker Initialization
        for worker_index in range(self.number_of_worker):
            app.logger.info(f'[+] Creating Worker-{worker_index}...')
            threading.Thread(target=self.task_assign, args=(worker_index,), daemon=True).start()
        app.logger.info(f'[+] Monolith (number of works = {self.number_of_worker}) is ready to accept tasks.')
        
        # Memory Monitoring
        threading.Thread(target=self.monitor_memory_usage, args=(10,), daemon=True).start()
    
    def monitor_memory_usage(self, interval=10):
        while True:
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024 ** 3)
            available_gb = mem.available / (1024 ** 3)
            app.logger.info(f"Memory usage: {mem.percent}% (Total: {total_gb} GB, Available: {available_gb} GB)")
            time.sleep(interval)
            
    def get_status(self) -> Dict[str, Any]:
        with self.task_results_lock:
            return {
                'max_queue_size': self.task_queue.maxsize,
                'current_queue_size': self.task_queue.qsize(),
                'max_result_cache_size': self.result_cache_size,
                'current_result_cache_size': len(self.task_results),
                'number_of_worker': self.number_of_worker,
                'worker_status': self.worker_status
            }
    
    def task_clean(self, result_cache_limit) -> None:
        with self.task_results_lock:
            app.logger.debug(f'[-] Cleaning task results: {len(self.task_results)}')
            while len(self.task_results) >= result_cache_limit:
                self.task_results.popitem(last=False)

    def task_assign(self, worker_id) -> None:
        app.logger.debug(f'[-] Worker-{worker_id} is ready to work.')
        while True:
            # Set the worker status to True (idle)
            with self.task_results_lock:
                self.worker_status[worker_id] = True
            
            # Wait for a task
            task_id, input_dict = self.task_queue.get()
            
            # Set the worker status to False (Occupied)
            with self.task_results_lock:
                self.worker_status[worker_id] = False
                
            task_result = {
                'task_id': task_id,
                'input_dict': input_dict,
                'worker_id': worker_id,
                'timestamp': time.time(),
                'process_time': float('inf'),
                'status': 'processing',
                'output_dict': None
            }
            app.logger.info(f'[-] Worker-{worker_id} is processing task-{task_id}...')

            try:
                # Register the task
                with self.task_results_lock:
                    self.task_results[task_id] = task_result
                    
                # Process the task
                processed_result = self.task_process(worker_id, input_dict, task_result)

                # Update the task
                with self.task_results_lock:
                    self.task_results[task_id] = processed_result
            except Exception as e:
                error_result = {
                    'status': 'error',
                    'output_dict': {'error': f"Error: {str(e)}"}
                }
                task_result.update(error_result)
                with self.task_results_lock:
                    self.task_results[task_id] = task_result
                app.logger.error(f'[!] Worker-{worker_id} encountered an error on processing task-{task_id}: {e}', exc_info=True)
            finally:
                self.task_clean(result_cache_limit=self.result_cache_size)
                self.task_queue.task_done()

    def task_process(self, worker_id: int, input_dict: Dict, task_result: Dict) -> Dict:
        start_time = time.time()
        try:
            code = input_dict['code']
            libraries = input_dict.get('libraries', [])
            language = input_dict['language']
            timeout = min(input_dict.get('timeout', 30), 120)
            run_profiling = input_dict.get('run_memory_profile', False)
            
            app.logger.info(f'[-] Worker-{worker_id} is assigned for task-{task_result["task_id"]}.')

            # Consider making sandbox parameters configurable
            with SandboxSession(lang=language, verbose=False, container_configs={"mem_limit": "1g", "cpuset_cpus": str(worker_id)}) as session:
                @timeout_decorator.timeout(timeout, use_signals=False)
                def setup_and_run():
                    session.setup(libraries=libraries)
                    
                    result = session.run(code=code, run_profiling=run_profiling)
                    app.logger.info(f'[-] Worker-{worker_id} finished task-{task_result["task_id"]}.')
                    return result

                result = setup_and_run()
                task_result['output_dict'] = result
                task_result['status'] = 'done'
                
        except timeout_decorator.timeout_decorator.TimeoutError:
            task_result['status'] = 'timeout'
            task_result['output_dict'] = {'error': 'Timeout reached.'}
        except Exception as e:
            task_result['status'] = 'error'
            task_result['output_dict'] = {'error': str(e), 'traceback': logging.exception(e)}
        finally:
            task_result['process_time'] = time.time() - start_time
            app.logger.info(f'[-] Worker-{worker_id} finished task-{task_result["task_id"]} in {task_result["process_time"]:.2f} ms.')
            return task_result
        
    def submit_task(self, task_id: str, input_dict: Dict) -> None:
        try:
            self.task_queue.put((task_id, input_dict), block=False)
        except queue.Full:
            app.logger.warning(f'[!] Task queue full. Unable to submit task {task_id}')
            raise queue.Full
        

# Hyperparameters
number_of_worker = 64
task_queue_size = 256
result_cache_size = 512

app = Flask(__name__)
app.manager = MonolithManager(number_of_worker=number_of_worker, queue_size=task_queue_size, result_cache_size=result_cache_size)
app.logger.info(f"Monolith Config: [number_of_worker = {number_of_worker}] [task_queue_size = {task_queue_size}] [result_cache_size = {result_cache_size}]")
app.logger.info('=============================================')

@app.route('/execute', methods=['POST'])
def handle_execute():
    input_dict = request.get_json()
    uuid_str = str(uuid.uuid4())
    app.logger.info(f'[+] Received an execute request: {input_dict}, Task ID: {uuid_str}, Current Queue Size: {app.manager.task_queue.qsize()}')

    if not input_dict or 'code' not in input_dict:
        return jsonify({'error': 'No code provided', 'status': 'error'}), 400
    
    try:
        app.manager.submit_task(uuid_str, input_dict)
        app.logger.info(f'[+] Task [{uuid_str}] is added to the task queue.')
    except queue.Full:
        return jsonify({'error': 'Task queue is full. Try again later.', 'status': 'error'}), 503

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
        app.logger.info(f'[-] Task [{task_id}] is removed from the task results.')
    
    return jsonify(result), 200

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(app.manager.get_status()), 200

@app.route('/')
def index():
    return redirect("https://huggingface.co/spaces/Elfsong/Monolith", code=302)


if __name__ == '__main__':
    app.run(port=8000, debug=False)
    