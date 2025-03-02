# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-03-01

import time
import utils
import threading
import pandas as pd
import streamlit as st
from code_editor import code_editor

# Title
st.title("_Mono:blue[lith]_")

# Language
lang = st.selectbox("Language?", utils.lang_map.keys(), help="the language for submission.")
language = utils.lang_map[lang][0]

# Libraries
lib_str = st.text_input("Library?", placeholder="Package A, Package B, ... , Package N", help="if any libraries are needed. Seperate with a comma.")
libraries = [lib.strip() for lib in lib_str.split(",")] if lib_str else None

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
code_prompt = utils.lang_map[lang][2]
response_dict = code_editor(code_prompt, lang=utils.lang_map[lang][0], height=[15,15], options={"wrap": False}, buttons=editor_buttons)

timeout = 30

if response_dict['type'] == 'submit':
    code = response_dict['text']
    my_bar = st.progress(0, text=f"Code Execution starts")
    with st.spinner('Ok, give me a sec...'):
        response = utils.post_task(language, code, libraries)
        task_id = response['task_id']
        st.write(f"Task ID: {task_id}")
    
        for ts in range(timeout+1):
            time.sleep(1)
            response = utils.get_result(task_id)
            if response['status'] in ['done', 'error', 'timeout']:
                break
            my_bar.progress(ts / timeout, text=f"Running ({ts}/{timeout}) s...")

    
    if response['output_dict'] and response['output_dict']['stdout']:
        st.success(response['output_dict']['stdout'])
    
    if response['output_dict'] and response['output_dict']['stderr']:
        st.success(response['output_dict']['stderr'])
    
    if response['status'] == "done":
        st.write(f"**Execution Time:** :blue[{response['output_dict']['duration']}] ms, **Peak Memory:** :blue[{response['output_dict']['peak_memory']}] kb, **Integral:** :blue[{response['output_dict']['integral']}] kb*ms")
        st.area_chart(pd.DataFrame(response['output_dict']['log'], columns=["timestemp", "memory"]), x='timestemp', y='memory')
    else:
        st.error(response)
