# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-04-06

import os
import psutil
import platform

def on_starting(server):
    server._worker_id_overload = set()


def nworkers_changed(server, new_value, old_value):
    server._worker_id_current_workers = new_value


def _next_worker_id(server):
    if server._worker_id_overload:
        return server._worker_id_overload.pop()
    in_use = set(w._worker_id for w in tuple(server.WORKERS.values()) if w.alive)
    free = set(range(1, server._worker_id_current_workers + 1)) - in_use
    return free.pop()


def on_reload(server):
    server._worker_id_overload = set(range(1, server.cfg.workers + 1))


def pre_fork(server, worker):
    worker._worker_id = _next_worker_id(server)
    server.log.info(f"[+] ========================================================")
    server.log.info(f"[+] Worker-{worker._worker_id} is starting.")


def post_fork(server, worker):
    pid = worker.pid
    worker_id = worker._worker_id
    cpu_id = -1
    server.log.info(f"[+] Worker-{worker_id} started -> PID {pid}.")
    
    # Set CPU affinity for the worker
    if platform.system().lower() == "linux":
        num_cpus = psutil.cpu_count(logical=True) or 1
        cpu_id = worker_id % num_cpus
        os.sched_setaffinity(pid, {cpu_id})
        server.log.info(f"[+] Worker-{worker_id} (PID {pid}) pinned to physical CPU core {cpu_id}.")
    else:
        server.log.info(f"[-] CPU affinity only works on Linux. Skipping...")
        
    # Set the worker ID in the environment variable
    os.environ["GUNICORN_WORKER_ID"] = str(worker_id)
    os.environ["GUNICORN_PROCESS_ID"] = str(pid)
    os.environ["GUNICORN_CPU_CORE_ID"] = str(cpu_id)
