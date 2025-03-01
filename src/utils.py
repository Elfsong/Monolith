# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2025-03-01

import time
import threading

lang_map = {
    "Python": ["python", "python", "# Don't Worry, You Can't Break It. We Promise.\n"],
    "CPP": ["c_cpp", "cpp", "// Don't Worry, You Can't Break It. We Promise.\n// For Cpp, please make sure the program lasts at least 1 ms.\n"],
    "Java": ["java", "java", "// Don't Worry, You Can't Break It. We Promise.\n"],
    "JavaScript": ["javascript", "javascript", "// Don't Worry, You Can't Break It. We Promise.\n"],
    "Golang": ["golang", "go", "// Don't Worry, You Can't Break It. We Promise.\n"]
}