#!/bin/bash

set -e

sleep 60
if [ "$BUILD" = "TRUE" ]; then
  exec python service.py --verbose --build_es=True
else
  exec python service.py --verbose
fi
