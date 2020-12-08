#!/bin/bash

cat $1 | bril2json | brili -t $2 | grep "^TRACE: " | cut -c7- | python3 $(dirname "$0")/recover_trace.py $1 | bril2txt > "${1%.bril}.traced.bril"
