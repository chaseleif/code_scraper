#! /usr/bin/env bash

cmd="PYTHONDONTWRITEBYTECODE=1 $(which python3) $(pwd)/scrape.py"
echo $cmd
eval $cmd
