#!/bin/bash
progName=$(basename "$0")
progDir=$(realpath "$0" | xargs dirname)
sed 's/ = /=/' "$progDir"/src/info.py
