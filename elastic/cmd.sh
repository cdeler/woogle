#!/bin/bash

set -e

sleep 60
exec python service.py --verbose --mapping="$MAPPING" --delete="$DELETE" --data="$DATA"