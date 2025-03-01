# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-03-01

import utils
import streamlit as st
from code_editor import code_editor

st.title("_Mono:blue[lith]_")

lang = st.selectbox("Language?", utils.lang_map.keys(), help="the language for submission.")

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
code = utils.lang_map[lang][2]
response_dict = code_editor(code, lang=utils.lang_map[lang][0], height=[15,15], options={"wrap": False}, buttons=editor_buttons)