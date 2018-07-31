#!/bin/bash

TIMEOUT=15
cmd=$(basename $0)
usage() {
  cat << USAGE >&2
Usage:
  $cmdname host:port [-t timeout] [-- command args]
  -t TIMEOUT                          Timeout in seconds, zero for no timeout
  -- COMMAND ARGS                     Execute command with args after the test finishes
USAGE
  exit 1
}

wait_for() {
  for i in `seq $TIMEOUT` ; do
    (echo > /dev/tcp/$HOST/$PORT) >/dev/null 2>&1
    result=$?
    if [[ $result -eq 0 ]] ; then
      if [[ $# -gt 0 ]] ; then
        echo "Postgres is up" >&2
        exec "$@"
      fi
      exit 0
    fi
    sleep 1
  done
  echo "Operation timed out" >&2
  exit 1
}

while [[ $# -gt 0 ]]
do
  case "$1" in
    *:* )
    hostport=(${1//:/ })
    HOST=${hostport[0]}
    PORT=${hostport[1]}
    shift 1
    ;;
    -t)
    TIMEOUT="$2"
    if [[ $TIMEOUT == "" ]]; then break; fi
    shift 2
    ;;
    --)
    shift
    break
    ;;
    --help)
    usage
    ;;
    *)
    printf "Unknown argument: $1"
    usage
    ;;
  esac
done

if [[ $HOST == "" || $PORT == "" ]]; then
  echo "Error: you need to provide a host and port to test."
  usage
fi
wait_for "$@"

