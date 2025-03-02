# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-03-01

import time
import requests
import pandas as pd
import streamlit as st
from code_editor import code_editor

lang_map = {
    "Python": ["python", "python", "# Don't Worry, You Can't Break It. We Promise.\n"],
    "CPP": ["c_cpp", "cpp", "// Don't Worry, You Can't Break It. We Promise.\n// For Cpp, please make sure the program lasts at least 1 ms.\n"],
    "Java": ["java", "java", "// Don't Worry, You Can't Break It. We Promise.\n"],
    "JavaScript": ["javascript", "javascript", "// Don't Worry, You Can't Break It. We Promise.\n"],
    "Golang": ["golang", "go", "// Don't Worry, You Can't Break It. We Promise.\n"]
}

def post_task(lang, code, libs=None, timeout=30, memory_profile=False):
    url = 'https://monolith.cool/execute'
    data = {'language': lang, 'code': code, 'libraries': libs, 'timeout': timeout, 'run_memory_profile': memory_profile}
    response = requests.post(url, json=data)
    return response.json()

def get_result(task_id):
    url = f'https://monolith.cool/results/{task_id}'
    response = requests.get(url)
    return response.json()

# Title
st.title("_Monolith_ is :blue[cool] :sunglasses:")

# Language
lang = st.selectbox("Language?", lang_map.keys(), help="the language for submission.")
language = lang_map[lang][0]

# Libraries
lib_str = st.text_input("Library?", placeholder="Package A, Package B, ... , Package N", help="if any libraries are needed. Seperate with a comma.")
libraries = [lib.strip() for lib in lib_str.split(",")] if lib_str else None

# Memory Profile
memory_profile = st.checkbox("Memory Profile?", help="Enable memory profiling for the code execution.")

# Timeout
timeout = st.number_input("Timeout?", min_value=1, max_value=120, value=30, help="the maximum time allowed for execution.")

# Code Editor
editor_buttons = [{
    "name": "Submit", 
    "feather": "Play",
    "primary": True, 
    "hasText": True, 
    "showWithIcon": True, 
    "commands": ["submit"], 
    "style": {"bottom": "0.44rem","right": "0.4rem"}
}]
code_prompt = lang_map[lang][2]
response_dict = code_editor(code_prompt, lang=lang_map[lang][0], height=[15,15], options={"wrap": False}, buttons=editor_buttons)

if response_dict['type'] == 'submit':
    code = response_dict['text']
    my_bar = st.progress(0, text=f"Code Execution starts")
    with st.spinner('Ok, give me a sec...'):
        response = post_task(language, code, libraries, 30, memory_profile)
        task_id = response['task_id']
        st.write(f"Task ID: {task_id}")
    
        for ts in range(timeout+1):
            time.sleep(1)
            response = get_result(task_id)
            if response['status'] in ['done', 'error', 'timeout']:
                break
            my_bar.progress(ts / timeout, text=f"Running ({ts}/{timeout}) s...")
    
    if response['output_dict'] and 'stdout' in response['output_dict']:
        st.success(response['output_dict']['stdout'])
    
    if response['output_dict'] and 'stderr' in response['output_dict']:
        st.warning(response['output_dict']['stderr'])
    
    if response['status'] == "done":
        if memory_profile:
            st.write(f"**Execution Time:** :blue[{response['output_dict']['duration']}] ms, **Peak Memory:** :blue[{response['output_dict']['peak_memory']}] kb, **Integral:** :blue[{response['output_dict']['integral']}] kb*ms")
            st.area_chart(pd.DataFrame(response['output_dict']['log'], columns=["timestemp", "memory"]), x='timestemp', y='memory')
        else:
            st.write(f"**Elapsed Time:** :blue[{response['output_dict']['time_v']['elapsed_time_seconds']}], **System Time:** :blue[{response['output_dict']['time_v']['system_time']}], **User Time:** :blue[{response['output_dict']['time_v']['user_time']}], **Peak Memory:** :blue[{response['output_dict']['time_v']['max_resident_set_kb']}] kb")

    else:
        st.error(response)
