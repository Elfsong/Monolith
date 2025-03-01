# code: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-01-11

import time
import threading
import numpy as np
import pandas as pd
import streamlit as st
from code_editor import code_editor
from llm_sandbox import SandboxSession


st.title("_Monolith_ is :blue[cool] :sunglasses:")
st.write('*It is a remote runtimes environment for code execution and evaluation. Please feel free to try [it](http://35.198.229.197:8000/docs#/default/execute_run_get) out!*')
st.write('*Any questions? Please contact :blue[mingzhe@nus.edu.sg]*')

lang_map = {
    "Python": ["python", "python", "# Don't Worry, You Can't Break It. We Promise.\n"],
    "CPP": ["c_cpp", "cpp", "// Don't Worry, You Can't Break It. We Promise.\n// For Cpp, please make sure the program lasts at least 1 ms.\n"],
    "Java": ["java", "java", "// Don't Worry, You Can't Break It. We Promise.\n"],
    "JavaScript": ["javascript", "javascript", "// Don't Worry, You Can't Break It. We Promise.\n"],
    "Golang": ["golang", "go", "// Don't Worry, You Can't Break It. We Promise.\n"]
}

lang = st.selectbox("Language?", lang_map.keys(), help="the language for submission.")

lib_str = st.text_input("Library?", placeholder="Package A, Package B, ... , Package N", help="if any libraries are needed. Seperate with a comma.")
libs = [lib.strip() for lib in lib_str.split(",")] if lib_str else None

editor_buttons = [{
    "name": "Submit", 
    "feather": "Play",
    "primary": True, 
    "hasText": True, 
    "showWithIcon": True, 
    "commands": ["submit"], 
    "style": {"bottom": "0.44rem","right": "0.4rem"}
}]

code = lang_map[lang][2]
response_dict = code_editor(code, lang=lang_map[lang][0], height=[15,15], options={"wrap": False}, buttons=editor_buttons)

def run_with_timeout(func, timeout, *args, **kwargs):
    """Runs a function with a timeout."""
    desc = kwargs['desc']
    result = {'output': None, 'error': None}
    my_bar = st.progress(0, text=f"{desc} starts")

    def target():
        try:
            result['output'] = func(*args, **kwargs)
        except Exception as e:
            result['error'] = e

    thread = threading.Thread(target=target)
    thread.start()
    
    for ts in range(timeout+1):
        time.sleep(1)
        if not thread.is_alive():
            my_bar.progress(ts / timeout, text=f"{desc} Finished.")
            break  # If the thread finishes, exit the loop
        my_bar.progress(ts / timeout, text=f"{desc} Running ({ts}/{timeout}) s...")
        ts += 1

    if thread.is_alive():
        thread.join(0)  # Clean up the thread
        result["error"] = 'Timeout Reached.'
        my_bar.progress(1.0, text=f"{desc} Timeout reached.")
    return result

if response_dict['type'] == 'submit':
    code = response_dict['text']
    with st.spinner('Ok, give me a sec...'):
        with SandboxSession(lang=lang_map[lang][1], verbose=True) as session:
            if libs:
                response = run_with_timeout(session.setup, 120, desc='Library Setup', libraries=libs)
            response = run_with_timeout(session.run, 60, code, True, desc='Code Execution', )
    
    if response['output'] and response['output']['stdout']:
        st.success(response['output']['stdout'])
            
    if response['error']:
        st.error(response['error'])
    elif response['output']['stderr']:
        st.error(response['output']['stderr'])
    else:
        st.write(f"**Execution Time:** :blue[{response['output']['duration']}] ms, **Peak Memory:** :blue[{response['output']['peak_memory']}] kb, **Integral:** :blue[{response['output']['integral']}] kb*ms")
        st.area_chart(pd.DataFrame(response['output']['log'], columns=["timestemp", "memory"]), x='timestemp', y='memory')

   
