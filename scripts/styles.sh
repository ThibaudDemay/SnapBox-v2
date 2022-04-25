#/usr/bin/env bash

OPTS=`getopt -o c --long check -n 'styles.sh' -- "$@"`

eval set -- "$OPTS"

# init default vars
CHECK=false

while true; do
  case "$1" in
    -c | --check ) CHECK=true; shift ;;
    * ) break ;;
  esac
done

if [[ $CHECK = true ]]; then
    pdm run black snapbox --check
    pdm run isort snapbox --check-only
else
    pdm run black snapbox
    pdm run isort snapbox
fi

pdm run pflake8 snapbox
