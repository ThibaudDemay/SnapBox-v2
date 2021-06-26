.DEFAULT_GOAL:= help

GREEN  := $(shell tput -Txterm setaf 2)
RESET  := $(shell tput -Txterm sgr0)

## Make styles with some tools (black, isort, flake8)
styles:
	black ./snapbox
	isort ./snapbox
	flake8

## Check if styles was correct (black, isort, flake8)
styles_check:
	black ./snapbox --check
	isort ./snapbox --check-only
	flake8

## Show this help
help:
	@printf "\nusage : make <commands> \n\nthe following commands are available : \n\n"
	@cat Makefile | awk '1;/help:/{exit}' | awk '/##/ { print; getline; print; }' | awk '{ getline x; print "${GREEN}" x "${RESET}"; }1' | awk '{ key=$$0; getline; print key "\t" $$0;}' | sed -e 's/##//' | sed -e 's/##//' | perl -ne 'printf "%-40s %s", /(.*)\t(.*)/s'
	@printf "\n"
