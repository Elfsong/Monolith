import re
import docker
import docker.errors
from typing import Optional

from docker import DockerClient
from llm_sandbox.const import SupportedLanguage


def image_exists(client: DockerClient, image: str) -> bool:
    """
    Check if a Docker image exists
    :param client: Docker client
    :param image: Docker image
    :return: True if the image exists, False otherwise
    """
    try:
        client.images.get(image)
        return True
    except docker.errors.ImageNotFound:
        return False
    except Exception as e:
        raise e


def get_libraries_installation_command(lang: str, library: str) -> Optional[str]:
    """
    Get the command to install libraries for the given language
    :param lang: Programming language
    :param library: List of libraries
    :return: Installation command
    """
    if lang == SupportedLanguage.PYTHON:
        return f"pip install {library}"
    elif lang == SupportedLanguage.JAVA:
        return f"mvn install:install-file -Dfile={library}"
    elif lang == SupportedLanguage.JAVASCRIPT:
        return f"yarn add {library}"
    elif lang == SupportedLanguage.CPP:
        return f"apt-get install {library}"
    elif lang == SupportedLanguage.GO:
        return f"go get -u {library}"
    elif lang == SupportedLanguage.RUBY:
        return f"gem install {library}"
    else:
        raise ValueError(f"Language {lang} is not supported")


def get_code_file_extension(lang: str) -> str:
    """
    Get the file extension for the given language
    :param lang: Programming language
    :return: File extension
    """
    if lang == SupportedLanguage.PYTHON:
        return "py"
    elif lang == SupportedLanguage.JAVA:
        return "java"
    elif lang == SupportedLanguage.JAVASCRIPT:
        return "js"
    elif lang == SupportedLanguage.CPP:
        return "cpp"
    elif lang == SupportedLanguage.GO:
        return "go"
    elif lang == SupportedLanguage.RUBY:
        return "rb"
    else:
        raise ValueError(f"Language {lang} is not supported")


def get_code_execution_command(lang: str, code_file: str, run_memory_profile: bool) -> list:
    """
    Return the execution command for the given language and code file.
    :param lang: Language of the code
    :param code_file: Path to the code file
    :return: List of execution commands
    """
    if run_memory_profile:
        if lang == SupportedLanguage.PYTHON:
            return [f"/tmp/memory_profiler.sh python {code_file}"]
        elif lang == SupportedLanguage.JAVA:
            return [f"/tmp/memory_profiler.sh java {code_file}"]
        elif lang == SupportedLanguage.JAVASCRIPT:
            return [f"/tmp/memory_profiler.sh node {code_file}"]
        elif lang == SupportedLanguage.CPP:
            return [f"g++ -o a.out {code_file}", "/tmp/memory_profiler.sh ./a.out"]
        elif lang == SupportedLanguage.GO:
            return [f"/tmp/memory_profiler.sh go run {code_file}"]
        elif lang == SupportedLanguage.RUBY:
            return [f"ruby {code_file}"]
        else:
            raise ValueError(f"Language {lang} is not supported")
    else:
        if lang == SupportedLanguage.PYTHON:
            return [f"python {code_file}"]
        elif lang == SupportedLanguage.JAVA:
            return [f"java {code_file}"]
        elif lang == SupportedLanguage.JAVASCRIPT:
            return [f"node {code_file}"]
        elif lang == SupportedLanguage.CPP:
            return [f"g++ -o a.out {code_file}", "./a.out"]
        elif lang == SupportedLanguage.GO:
            return [f"go run {code_file}"]
        elif lang == SupportedLanguage.RUBY:
            return [f"ruby {code_file}"]
        else:
            raise ValueError(f"Language {lang} is not supported")
    


def parse_time_v_output(time_v_text: str) -> dict:
    """
    Parse the text output from `time -v` (GNU time verbose mode)
    and return a dictionary with structured data.
    
    Example usage:
        with open("time_v_output.txt") as f:
            output = f.read()
        stats = parse_time_v_output(output)
        print(stats)
    """
    stats = {}
    
    # Regex patterns to capture various fields
    cmd_pattern          = re.compile(r'^Command being timed: "(.*)"')
    user_time_pattern    = re.compile(r'^User time \(seconds\): ([\d.]+)')
    system_time_pattern  = re.compile(r'^System time \(seconds\): ([\d.]+)')
    cpu_percent_pattern  = re.compile(r'^Percent of CPU this job got: (\d+)%')
    elapsed_time_pattern = re.compile(r'^Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (.*)')
    
    # Helper function to parse the "h:mm:ss" or "m:ss" style time
    def parse_h_m_s(time_str: str) -> float:
        """
        Convert a time string of the form H:MM:SS or M:SS or S into a total number of seconds as float.
        """
        parts = time_str.split(':')
        if len(parts) == 3:
            # hours:minutes:seconds
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            # minutes:seconds
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            # just seconds
            return float(time_str)
    
    # Go line by line, match against known patterns, or do simple splits:
    for line in time_v_text.splitlines():
        line = line.strip()
        
        # Check regex-based lines first
        if match := cmd_pattern.match(line):
            stats["command"] = match.group(1)
        elif match := user_time_pattern.match(line):
            stats["user_time"] = float(match.group(1))
        elif match := system_time_pattern.match(line):
            stats["system_time"] = float(match.group(1))
        elif match := cpu_percent_pattern.match(line):
            stats["cpu_percent"] = int(match.group(1))
        elif match := elapsed_time_pattern.match(line):
            raw_elapsed = match.group(1)
            stats["elapsed_time_seconds"] = parse_h_m_s(raw_elapsed)
            
        # Simple split-based matches (key: value)
        elif "Maximum resident set size (kbytes):" in line:
            _, val = line.split(":", 1)
            stats["max_resident_set_kb"] = int(val.strip())
        elif "Average shared text size (kbytes):" in line:
            _, val = line.split(":", 1)
            stats["avg_shared_text_kb"] = int(val.strip())
        elif "Average unshared data size (kbytes):" in line:
            _, val = line.split(":", 1)
            stats["avg_unshared_data_kb"] = int(val.strip())
        elif "Average stack size (kbytes):" in line:
            _, val = line.split(":", 1)
            stats["avg_stack_size_kb"] = int(val.strip())
        elif "Average total size (kbytes):" in line:
            _, val = line.split(":", 1)
            stats["avg_total_size_kb"] = int(val.strip())
        elif "Minor (reclaiming a frame) page faults:" in line:
            _, val = line.split(":", 1)
            stats["minor_page_faults"] = int(val.strip())
        elif "Major (requiring I/O) page faults:" in line:
            _, val = line.split(":", 1)
            stats["major_page_faults"] = int(val.strip())
        elif "Voluntary context switches:" in line:
            _, val = line.split(":", 1)
            stats["voluntary_context_switches"] = int(val.strip())
        elif "Involuntary context switches:" in line:
            _, val = line.split(":", 1)
            stats["involuntary_context_switches"] = int(val.strip())
        elif "Swaps:" in line:
            _, val = line.split(":", 1)
            stats["swaps"] = int(val.strip())
        elif "File system inputs:" in line:
            _, val = line.split(":", 1)
            stats["file_system_inputs"] = int(val.strip())
        elif "File system outputs:" in line:
            _, val = line.split(":", 1)
            stats["file_system_outputs"] = int(val.strip())
        elif "Signals delivered:" in line:
            _, val = line.split(":", 1)
            stats["signals_delivered"] = int(val.strip())
        elif "Socket messages sent:" in line:
            _, val = line.split(":", 1)
            stats["socket_messages_sent"] = int(val.strip())
        elif "Socket messages received:" in line:
            _, val = line.split(":", 1)
            stats["socket_messages_received"] = int(val.strip())
        elif "Page size (bytes):" in line:
            _, val = line.split(":", 1)
            stats["page_size_bytes"] = int(val.strip())
        elif "Exit status:" in line:
            _, val = line.split(":", 1)
            stats["exit_status"] = int(val.strip())

    return stats