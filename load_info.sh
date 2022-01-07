#!/bin/bash
progName=$(basename "$0")
progDir=$(realpath "$0" | xargs dirname)
sed 's/[[:space:]]*=[[:space:]]*/=/' "$progDir"/src/info.py
