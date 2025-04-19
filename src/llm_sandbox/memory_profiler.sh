#!/usr/bin/env bash

# Usage
if [ $# -lt 1 ]; then
  echo "Usage: $0 <command> [args...]"
  exit 1
fi

# Save commands as an array
CMD=("$@")

# Set log name
LOG_FILE="mem_usage.log"

exec 3<&0
exec </dev/null

# Get PID
"${CMD[@]}" <&3 & 
PID=$!
exec 3<&-   

while kill -0 "$PID" 2>/dev/null; do
    timestamp_ns=$(date +%s%N)
    
    rss_kb=$(awk '/VmRSS/{print $2}' /proc/$PID/status 2>/dev/null)
    if [ -z "$rss_kb" ]; then
        rss_kb=0
    fi
    
    echo "$timestamp_ns $rss_kb" >> "$LOG_FILE"
done

# 5. Wait PID finish
wait $PID 2>/dev/null