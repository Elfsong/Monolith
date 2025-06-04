# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-04-06

import os
import uuid
import psutil
import logging
import traceback
import timeout_decorator

from llm_sandbox import SandboxSession
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, redirect
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, TimeoutError

# Logging Configuration
log_handler = RotatingFileHandler(
    filename='monolith.log',
    maxBytes=100 * 1024 * 1024,
    backupCount=5
)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
log_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.handlers.clear()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

worker_id = int(os.getenv("GUNICORN_WORKER_ID", "0"))
cpu_core_id = int(os.getenv("GUNICORN_CPU_CORE_ID", "0"))
logger.info(f"[+] Worker-{worker_id} started on CPU-{cpu_core_id}.")

@app.route('/')
def index():
    logger.info(f"[+] Worker-{worker_id} received a request to index.")
    return redirect("https://huggingface.co/spaces/Elfsong/Monolith", code=302)

@app.errorhandler(Exception)
def handle_global_exception(e):
    logger.exception("[!!] Unhandled exception in Flask app")
    return jsonify({
        "status": "error",
        "error": str(e),
        "trace": traceback.format_exc()
    }), 500

    
@app.route('/execute', methods=['POST'])
def handle_execute():
    try:
        input_dict = request.get_json() or {}
        code = input_dict.get("code")
        language = input_dict.get("language")
        
        # Input Validation
        if not code: return jsonify({"status": "error", "error": "No code provided"}), 400
        if not language: return jsonify({"status": "error", "error": "No language provided"}), 400
        
        # Metadata
        task_id = str(uuid.uuid4())
        logger.info(f"[+] Worker-{worker_id} is processing the request ({task_id}) on CPU-{cpu_core_id}: {input_dict}")
        
        # Task Execution
        response = task_process(input_dict, cpu_core_id, task_id)
        logger.info(f"[+] Worker-{worker_id} finished processing the request ({task_id})")
        
        return jsonify(response), 200
    except Exception as e:
        logger.exception("handle_execute failed")
        return jsonify({"status": "error", "error": str(e)}), 500


def task_process(input_dict: dict, cpu_core_id: int, task_id: str) -> dict:
    # Task Attributes
    code = input_dict['code']
    libraries = input_dict.get('libraries', [])
    language = input_dict['language']
    timeout = min(input_dict.get('timeout', 30), 120)
    run_profiling = input_dict.get('run_profiling', False)
    stdin = input_dict.get('stdin', None)
    
    # Docker Container Configuration
    container_configs = {
        "mem_limit": "1g",
        "mem_swappiness": 0,
        "memswap_limit": "1g",
        "oom_kill_disable": False,
        "cpuset_cpus": str(cpu_core_id)
    }
    
    # Response Initialization
    response = {
        'task_id': task_id,
        'output_dict': None,
        'status': 'error',
        'error': None,
    }
    
    # Sandbox Execution
    session = SandboxSession(lang=language, verbose=False, container_configs=container_configs)
    try:
        session.open()
        logger.info(f"[+] Worker-{worker_id} created a new session container {session.container.name}")

        @timeout_decorator.timeout(timeout, use_signals=False)
        def setup_and_run(libraries, code, stdin, run_profiling):
            session.setup(libraries=libraries, run_profiling=run_profiling)
            return session.run(code=code, stdin=stdin, run_profiling=run_profiling)

        try:
            result = setup_and_run(libraries, code, stdin, run_profiling)
            response['output_dict'] = result
            response['status'] = 'success'
        except TimeoutError:
            response['status'] = 'timeout'
            response['error'] = 'Task timed out.'
        except Exception as e:
            response['error'] = str(e)

    except Exception as e:
        logger.error(f"[!!] Sandbox setup failed ({task_id})")
        response['error'] = str(e)
    finally:
        try:
            session.close()
        except Exception as cleanup_error:
            logger.error(f"Failed to clean up container: {cleanup_error}")
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

