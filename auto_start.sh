#! /bin/bash
eval "$(conda shell.bash hook)"
conda activate monolith
cd Projects/Monolith
./stop.sh
./start.sh
echo 'bingo'
